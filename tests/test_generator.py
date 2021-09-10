#!/usr/bin/env python3

# Copyright (c) 2021 - 2021 TomTom N.V.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import llvm_diagnostics
from llvm_diagnostics.messages import DiagnosticsLevel, DiagnosticsMessage
import pytest
from unittest.mock import Mock

from bitbucket_code_insight_reporter import generate


@pytest.mark.parametrize(
    "input, expectation",
    (
        ("error", "HIGH"),
        ("warning", "MEDIUM"),
        ("note", "LOW"),
        ("random_string", "LOW"),
        (123, "LOW"),
    ),
)
def test_get_severity_for_level(input, expectation):
    assert generate.get_severity_for_level(input) == expectation


def test_retrieve_annotations_from_file():
    llvm_diagnostics.parser.diagnostics_messages_from_file = Mock(
        return_value=[
            DiagnosticsMessage(
                "first_test.py", 1, 1, "test message", DiagnosticsLevel.ERROR
            ),
            DiagnosticsMessage(
                "second_test.py", 2, 2, "test message", DiagnosticsLevel.WARNING
            ),
        ]
    )

    _expectations = [
        {
            "path": "first_test.py",
            "message": "test message",
            "line": 1,
            "severity": "HIGH",
        },
        {
            "path": "second_test.py",
            "message": "test message",
            "line": 2,
            "severity": "MEDIUM",
        },
    ]

    assert generate.retrieve_annotations_from_file(None, None) == _expectations


def test_retrieve_annotations_from_empty_file():
    llvm_diagnostics.parser.diagnostics_messages_from_file = Mock(return_value=[])
    assert generate.retrieve_annotations_from_file(None, None) == []


def test_retrieve_annotations_from_file_workspace():
    llvm_diagnostics.parser.diagnostics_messages_from_file = Mock(
        return_value=[DiagnosticsMessage("/code/first_test.py", 1, 1, "test message")]
    )

    _expectations = [
        {
            "path": "first_test.py",
            "message": "test message",
            "line": 1,
            "severity": "HIGH",
        }
    ]

    assert generate.retrieve_annotations_from_file(None, "/code/") == _expectations


def test_retrieve_annotations_from_file_wrong_workspace():
    llvm_diagnostics.parser.diagnostics_messages_from_file = Mock(
        return_value=[DiagnosticsMessage("/code/first_test.py", 1, 1, "test message")]
    )

    _expectations = [
        {
            "path": "/code/first_test.py",
            "message": "test message",
            "line": 1,
            "severity": "HIGH",
        }
    ]

    assert (
        generate.retrieve_annotations_from_file(None, "/wrong_workspace/")
        == _expectations
    )


def test_validate_no_annotations():
    llvm_diagnostics.parser.diagnostics_messages_from_file = Mock(return_value=[])
    data = generate.create_report(
        id="test_report",
        workspace=None,
        llvm_logging="/code/",
    )

    _expectations = {"id": "test_report", "report": {"result": "PASS"}}

    assert data == _expectations


def test_validate_annotations():
    llvm_diagnostics.parser.diagnostics_messages_from_file = Mock(
        return_value=[DiagnosticsMessage("/code/first_test.py", 1, 1, "test message")]
    )
    data = generate.create_report(
        id="test_report",
        workspace=None,
        llvm_logging="/code/",
    )

    _expectations = {
        "id": "test_report",
        "report": {"result": "FAIL"},
        "annotations": [
            {
                "line": 1,
                "message": "test message",
                "path": "/code/first_test.py",
                "severity": "HIGH",
            }
        ],
    }

    assert data == _expectations


def test_validate_too_many_annotations():
    llvm_diagnostics.parser.diagnostics_messages_from_file = Mock(
        return_value=[
            DiagnosticsMessage("/code/first_test.py", 1, 1, "test message")
            for i in range(1001)
        ]
    )
    data = generate.create_report(
        id="test_report",
        workspace=None,
        llvm_logging="/code/",
    )

    _expectations = {
        "id": "test_report",
        "report": {
            "details": "NOTE: The number of code annotations (1001) exceeded the limit (1000)!",
            "result": "FAIL",
        },
    }

    assert data == _expectations
