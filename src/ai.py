#!/usr/bin/env python3
"""
AI module for TutorAI
Handles all GPT/OpenAI related functionality including help and evaluation.
"""

from openai import OpenAI
from logger import log_app_event


def help_gpt(q, code, error, app_logger=None):
    """Stream help from GPT."""
    messages = [
        {"role": "system", "content": "you are an expert python tutor and help kids 10 year old to learn python, and suggest solution for question q based on code and error of code execution, provide easy to understand explaination for kid in not more than 5 lines, you must guide to get to right solution without providing actual solution"},
        {"role": "user", "content": "question: "+q + " code: "+ code + " output: "+error}
    ]
    stream = OpenAI().chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        stream=True
    )
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
        yield result


def evaluate_gpt(q, code, app_logger=None):
    """Stream evaluation from GPT for student's code solution."""
    if app_logger:
        log_app_event(app_logger, 'INFO', 'evaluate_gpt called', f"Question: {q[:50]}... | Code: {code[:50]}...")
    messages = [
        {"role": "system", "content": "you are an expert python tutor and help kids 10 year old to learn python, evaluate solution of q as provided on code, if its about expected output, Say Good Job, otherwise provide hint on what is expected without providing actual solution "},
        {"role": "user", "content": "question: "+q + " code: "+ code }
    ]
    try:
        stream = OpenAI().chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            stream=True
        )
        result = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            result += content
            if app_logger:
                log_app_event(app_logger, 'DEBUG', f'evaluate_gpt chunk: {len(content)} chars')
            yield result
        if app_logger:
            log_app_event(app_logger, 'INFO', 'evaluate_gpt completed', f"Final result length: {len(result)}")
    except Exception as e:
        if app_logger:
            log_app_event(app_logger, 'ERROR', 'evaluate_gpt failed', f"Error: {str(e)}")
        yield f"AI Evaluation Error: {str(e)}"


def evaluate_gpt_sync(q, code, app_logger=None):
    """Non-streaming evaluation from GPT for Docker environments."""
    if app_logger:
        log_app_event(app_logger, 'INFO', 'evaluate_gpt_sync called', f"Question: {q[:50]}... | Code: {code[:50]}...")
    messages = [
        {"role": "system", "content": "you are an expert python tutor and help kids 10 year old to learn python, evaluate solution of q as provided on code, if its about expected output, Say Good Job, otherwise provide hint on what is expected without providing actual solution "},
        {"role": "user", "content": "question: "+q + " code: "+ code }
    ]
    try:
        completion = OpenAI().chat.completions.create(
            model='gpt-4o-mini',
            messages=messages
        )
        result = completion.choices[0].message.content
        if app_logger:
            log_app_event(app_logger, 'INFO', 'evaluate_gpt_sync completed', f"Result length: {len(result)}")
        return result
    except Exception as e:
        if app_logger:
            log_app_event(app_logger, 'ERROR', 'evaluate_gpt_sync failed', f"Error: {str(e)}")
        return f"AI Evaluation Error: {str(e)}"

