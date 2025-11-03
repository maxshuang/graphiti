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


class NodeDuplicate(BaseModel):
    id: int = Field(..., description='integer id of the entity')
    duplicate_idx: int = Field(
        ...,
        description='idx of the duplicate entity. If no duplicate entities are found, default to -1.',
    )
    name: str = Field(
        ...,
        description='Name of the entity. Should be the most complete and descriptive name of the entity. Do not include any JSON formatting in the Entity name such as {}.',
    )
    duplicates: list[int] = Field(
        ...,
        description='idx of all entities that are a duplicate of the entity with the above id.',
    )


class NodeResolutions(BaseModel):
    entity_resolutions: list[NodeDuplicate] = Field(..., description='List of resolved nodes')


class Prompt(Protocol):
    node: PromptVersion
    node_list: PromptVersion
    nodes: PromptVersion


class Versions(TypedDict):
    node: PromptFunction
    node_list: PromptFunction
    nodes: PromptFunction


def node(context: dict[str, Any]) -> list[Message]:
    return [
        Message(
            role='system',
            content='You are a helpful assistant that determines whether or not a NEW ENTITY is a duplicate of any EXISTING ENTITIES.',
        ),
        Message(
            role='user',
            content=f"""
        <NEW ENTITY>
        {to_prompt_json(context['extracted_node'], ensure_ascii=context.get('ensure_ascii', False), indent=2)}
        </NEW ENTITY>

        <EXISTING ENTITIES>
        {to_prompt_json(context['existing_nodes'], ensure_ascii=context.get('ensure_ascii', False), indent=2)}
        </EXISTING ENTITIES>

        Determine if the NEW ENTITY is a duplicate of any entity in EXISTING ENTITIES.

        Two entities are duplicates ONLY if ALL of these conditions are met:
        1. IDENTICAL entity_type labels (excluding 'Entity')
        2. IDENTICAL semantic meaning - read the actual field values to verify what each entity represents
        3. Measure or describe the SAME aspects (not just related to the same subject)

        Important:
        - Name similarity alone is NOT sufficient - similar names can represent different things
        - Same subject + same time period is NOT sufficient - one subject can have multiple different measurements
        - You MUST read the actual content in fields (not just field names) to determine if entities measure/describe the same thing
        - When in doubt, do NOT merge

        Respond with a JSON object containing an "entity_resolutions" array with a single entry:
        {{
            "entity_resolutions": [
                {{
                    "id": integer id from NEW ENTITY,
                    "name": the best full name for the entity,
                    "duplicate_idx": integer index of the best duplicate in EXISTING ENTITIES, or -1 if none,
                    "duplicates": sorted list of all duplicate indices you collected (deduplicate the list, use [] when none)
                }}
            ]
        }}

        Only reference indices that appear in EXISTING ENTITIES, and return [] / -1 when unsure.
        """,
        ),
    ]


def nodes(context: dict[str, Any]) -> list[Message]:
    return [
        Message(
            role='system',
            content='You are a helpful assistant that determines whether or not ENTITIES extracted from a conversation are duplicates'
            ' of existing entities. You MUST ONLY merge entities that have identical entity_type labels.',
        ),
        Message(
            role='user',
            content=f"""
        <ENTITIES>
        {to_prompt_json(context['extracted_nodes'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
        </ENTITIES>

        <EXISTING ENTITIES>
        {to_prompt_json(context['existing_nodes'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}
        </EXISTING ENTITIES>

        For each entity in ENTITIES, determine if it is a duplicate of any entity in EXISTING ENTITIES.

        Two entities are duplicates ONLY if ALL of these conditions are met:
        1. IDENTICAL entity_type labels (excluding 'Entity')
        2. IDENTICAL semantic meaning - read the actual field values to verify what each entity represents
        3. Measure or describe the SAME aspects (not just related to the same subject)

        Important:
        - Name similarity alone is NOT sufficient - similar names can represent different things
        - Same subject + same time period is NOT sufficient - one subject can have multiple different measurements
        - You MUST read the actual content in fields (not just field names) to determine if entities measure/describe the same thing
        - When in doubt, do NOT merge

        Task:
        Respond with a JSON object that contains an "entity_resolutions" array with one entry for each entity in ENTITIES, ordered by the entity id.

        For every entity, return an object with the following keys:
        {{
            "id": integer id from ENTITIES,
            "name": the best full name for the entity (preserve the original name unless a duplicate has a more complete name),
            "duplicate_idx": the idx of the EXISTING ENTITY that is the best duplicate match, or -1 if there is no duplicate,
            "duplicates": a sorted list of all idx values from EXISTING ENTITIES that refer to duplicates (deduplicate the list, use [] when none or unsure)
        }}

        - Only use idx values that appear in EXISTING ENTITIES.
        - Set duplicate_idx to the smallest idx you collected for that entity, or -1 if duplicates is empty.
        - Never fabricate entities or indices.
        """,
        ),
    ]


def node_list(context: dict[str, Any]) -> list[Message]:
    return [
        Message(
            role='system',
            content='You are a helpful assistant that de-duplicates nodes from node lists.',
        ),
        Message(
            role='user',
            content=f"""
        Given the following context, deduplicate a list of nodes:

        Nodes:
        {to_prompt_json(context['nodes'], ensure_ascii=context.get('ensure_ascii', True), indent=2)}

        Task:
        1. Group nodes together such that all duplicate nodes are in the same list of uuids
        2. All duplicate uuids should be grouped together in the same list
        3. Also return a new summary that synthesizes the summary into a new short summary

        Guidelines:
        1. Each uuid from the list of nodes should appear EXACTLY once in your response
        2. If a node has no duplicates, it should appear in the response in a list of only one uuid

        Respond with a JSON object in the following format:
        {{
            "nodes": [
                {{
                    "uuids": ["5d643020624c42fa9de13f97b1b3fa39", "node that is a duplicate of 5d643020624c42fa9de13f97b1b3fa39"],
                    "summary": "Brief summary of the node summaries that appear in the list of names."
                }}
            ]
        }}
        """,
        ),
    ]


versions: Versions = {'node': node, 'node_list': node_list, 'nodes': nodes}
