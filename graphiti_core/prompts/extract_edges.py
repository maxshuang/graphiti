"""
Copyright 2024, Zep Software, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Any, Protocol, TypedDict

from pydantic import BaseModel, Field

from .models import Message, PromptFunction, PromptVersion
from .prompt_helpers import to_prompt_json


class Edge(BaseModel):
    relation_type: str = Field(..., description='FACT_PREDICATE_IN_SCREAMING_SNAKE_CASE')
    source_entity_id: int = Field(..., description='The id of the source entity of the fact.')
    target_entity_id: int = Field(..., description='The id of the target entity of the fact.')
    fact: str = Field(..., description='')
    valid_at: str | None = Field(
        None,
        description='The date and time when the relationship described by the edge fact became true or was established. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS.SSSSSSZ)',
    )
    invalid_at: str | None = Field(
        None,
        description='The date and time when the relationship described by the edge fact stopped being true or ended. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS.SSSSSSZ)',
    )


class ExtractedEdges(BaseModel):
    edges: list[Edge]


class MissingFacts(BaseModel):
    missing_facts: list[str] = Field(..., description="facts that weren't extracted")


class Prompt(Protocol):
    edge: PromptVersion
    reflexion: PromptVersion
    extract_attributes: PromptVersion


class Versions(TypedDict):
    edge: PromptFunction
    reflexion: PromptFunction
    extract_attributes: PromptFunction


def edge(context: dict[str, Any]) -> list[Message]:
    return [
        Message(
            role='system',
            content='You are an expert fact extractor that extracts fact triples from text. '
            '1. Extracted fact triples should also be extracted with relevant date information.'
            '2. Treat the CURRENT TIME as the time the CURRENT MESSAGE was sent. All temporal information should be extracted relative to this time.',
        ),
        Message(
            role='user',
            content=f"""
<FACT TYPES>
{to_prompt_json(context['edge_types'], ensure_ascii=context.get('ensure_ascii', False), indent=2)}
</FACT TYPES>

<PREVIOUS_MESSAGES>
{to_prompt_json([ep for ep in context['previous_episodes']], ensure_ascii=context.get('ensure_ascii', False), indent=2)}
</PREVIOUS_MESSAGES>

<CURRENT_MESSAGE>
{context['episode_content']}
</CURRENT_MESSAGE>

<ENTITIES>
{to_prompt_json(context['nodes'], ensure_ascii=context.get('ensure_ascii', False), indent=2)}
</ENTITIES>

<REFERENCE_TIME>
{context['reference_time']}  # ISO 8601 (UTC); used to resolve relative time mentions
</REFERENCE_TIME>

# TASK
Extract factual relationships between the given ENTITIES based on the CURRENT MESSAGE.

**STEP 1 - CHECK IF FACT TYPES PROVIDED**:
- If FACT TYPES list is empty → you may use generic relation_type names
- If FACT TYPES list is NOT empty → YOU MUST FOLLOW STEPS 2-4 BELOW

**STEP 2 - UNDERSTAND FACT_TYPE_SIGNATURE DIRECTION**:
The fact_type_signature is an array: [SOURCE_TYPE, TARGET_TYPE]
- First element = source entity type (where arrow starts FROM)
- Second element = target entity type (where arrow points TO)
- Example: ["MetricObservation", "DataSource"] means:
  * SOURCE entity must be MetricObservation
  * TARGET entity must be DataSource
  * Direction: MetricObservation → DataSource

**STEP 3 - MANDATORY TYPE MATCHING** (if FACT TYPES provided):
For each potential relationship, you MUST:
a) Identify source entity's type (excluding 'Entity' label)
b) Identify target entity's type (excluding 'Entity' label)
c) Check if ANY FACT TYPE has fact_type_signature where:
   - fact_type_signature[0] == source entity type
   - fact_type_signature[1] == target entity type
d) If NO EXACT MATCH → DO NOT extract this relationship

**STEP 4 - USE EXACT RELATION NAME** (if FACT TYPES provided):
- Use the EXACT fact_type_name from the matching FACT TYPE
- Example: If FACT TYPE says "DERIVED_FROM" → use "DERIVED_FROM"
- NEVER use generic names like "RELATES_TO" when FACT TYPES are provided

**STEP 5 - REJECT INVALID RELATIONSHIPS** (if FACT TYPES provided):
DO NOT extract relationships that:
- Have entity types NOT matching any fact_type_signature IN THE CORRECT ORDER
- Connect entities of same type (unless explicitly in FACT TYPES)
- Use relation_type names not in FACT TYPES list
- Have reversed direction (signature[0] must be source, signature[1] must be target)

You may use information from the PREVIOUS MESSAGES only to disambiguate references or support continuity.

**EXAMPLE** (if FACT TYPES provided):

FACT TYPES: [
  {{"fact_type_name": "DERIVED_FROM", "fact_type_signature": ["MetricObservation", "DataSource"], ...}}
]

This means: MetricObservation (source) → DataSource (target)

ENTITIES: [
  {{"id": 0, "name": "Store A Metrics", "entity_types": ["Entity", "MetricObservation"]}},
  {{"id": 1, "name": "Sales_Data.csv", "entity_types": ["Entity", "DataSource"]}}
]

✅ CORRECT extraction:
{{
  "relation_type": "DERIVED_FROM",
  "source_entity_id": 0,  # MetricObservation (matches signature[0])
  "target_entity_id": 1   # DataSource (matches signature[1])
}}

❌ WRONG extractions:
1. Using wrong relation name:
   {{"relation_type": "RELATES_TO", "source_entity_id": 0, "target_entity_id": 1}}
   (RELATES_TO not in FACT TYPES)

2. Reversed direction:
   {{"relation_type": "DERIVED_FROM", "source_entity_id": 1, "target_entity_id": 0}}
   (DataSource → MetricObservation doesn't match signature ["MetricObservation", "DataSource"])

3. Wrong entity types:
   {{"relation_type": "DERIVED_FROM", "source_entity_id": 0, "target_entity_id": 0}}
   (MetricObservation → MetricObservation doesn't match signature)

{context['custom_prompt']}

# EXTRACTION RULES

1. Only emit facts where both the subject and object match IDs in ENTITIES.
2. Each fact must involve two **distinct** entities.
3. **CRITICAL**: If FACT TYPES are provided, ONLY extract facts that match one of the FACT TYPES:
   a. Check the source entity type matches the first element of fact_type_signature
   b. Check the target entity type matches the second element of fact_type_signature
   c. Use the EXACT relation_type name from FACT TYPES (not generic names like "RELATES_TO")
   d. If no FACT TYPE matches the entity types involved, DO NOT extract that relationship
4. If FACT TYPES are NOT provided (empty list), use a SCREAMING_SNAKE_CASE string as the `relation_type` (e.g., FOUNDED, WORKS_AT).
5. Do not emit duplicate or semantically redundant facts.
6. The `fact_text` should closely paraphrase the original source sentence(s). Do not verbatim quote the original text.
7. Use `REFERENCE_TIME` to resolve vague or relative temporal expressions (e.g., "last week").
8. Do **not** hallucinate or infer temporal bounds from unrelated events.

# DATETIME RULES

- Use ISO 8601 with “Z” suffix (UTC) (e.g., 2025-04-30T00:00:00Z).
- If the fact is ongoing (present tense), set `valid_at` to REFERENCE_TIME.
- If a change/termination is expressed, set `invalid_at` to the relevant timestamp.
- Leave both fields `null` if no explicit or resolvable time is stated.
- If only a date is mentioned (no time), assume 00:00:00.
- If only a year is mentioned, use January 1st at 00:00:00.
        """,
        ),
    ]


def reflexion(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """You are an AI assistant that determines which facts have not been extracted from the given context"""

    user_prompt = f"""
<PREVIOUS MESSAGES>
{to_prompt_json([ep for ep in context['previous_episodes']], ensure_ascii=context.get('ensure_ascii', False), indent=2)}
</PREVIOUS MESSAGES>
<CURRENT MESSAGE>
{context['episode_content']}
</CURRENT MESSAGE>

<EXTRACTED ENTITIES>
{context['nodes']}
</EXTRACTED ENTITIES>

<EXTRACTED FACTS>
{context['extracted_facts']}
</EXTRACTED FACTS>

Given the above MESSAGES, list of EXTRACTED ENTITIES entities, and list of EXTRACTED FACTS; 
determine if any facts haven't been extracted.
"""
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


def extract_attributes(context: dict[str, Any]) -> list[Message]:
    return [
        Message(
            role='system',
            content='You are a helpful assistant that extracts fact properties from the provided text.',
        ),
        Message(
            role='user',
            content=f"""

        <MESSAGE>
        {to_prompt_json(context['episode_content'], ensure_ascii=context.get('ensure_ascii', False), indent=2)}
        </MESSAGE>
        <REFERENCE TIME>
        {context['reference_time']}
        </REFERENCE TIME>

        Given the above MESSAGE, its REFERENCE TIME, and the following FACT, update any of its attributes based on the information provided
        in MESSAGE. Use the provided attribute descriptions to better understand how each attribute should be determined.

        Guidelines:
        1. Do not hallucinate entity property values if they cannot be found in the current context.
        2. Only use the provided MESSAGES and FACT to set attribute values.

        <FACT>
        {context['fact']}
        </FACT>
        """,
        ),
    ]


versions: Versions = {
    'edge': edge,
    'reflexion': reflexion,
    'extract_attributes': extract_attributes,
}
