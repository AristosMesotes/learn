"""
messages.py

This module defines classes and functions for managing conversation messages (IThought and its subclasses)
along with ephemeral-lazy loading of their embeddings and knowledge triples. It also provides utilities for
embedding storage, triple extraction stubs, and normalizing various message inputs into TextThought objects.
"""
import copy
import json
from typing import List
import logging
from typing import get_origin
from learn.thought.ithought import IThought
from learn.thought.text_thought import TextThought


def normalize_thoughts(messages: List[IThought]) -> List[IThought]:
    """
    Normalize heterogeneous message inputs into IThought instances.
    LLM clients call this so lists, strings or dicts become uniform objects.
    Ensures Node AI pipelines required operate on a consistent message format.
    """
    messages = copy.deepcopy(messages)
    if not messages:
        return []

    from_msg_type = get_origin(messages)
    if isinstance(messages, type) or from_msg_type is not None:
        return []

    if not isinstance(messages, list):
        messages = [messages]

    output_messages = []
    for i in range(len(messages)):
        if isinstance(messages[i], dict):

            output_messages.append(TextThought(json.dumps(messages[i], indent=4)))
        elif isinstance(messages[i], str):

            output_messages.append(TextThought(messages[i]))
        elif isinstance(messages[i], list):

            list_of_messages = normalize_thoughts(messages[i])
            if list_of_messages:
                output_messages.extend(list_of_messages)
        else:

            output_messages.append(messages[i])

    return output_messages
