#!/usr/bin/env python3
# Copyright The Kubeflow Authors.
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
"""Find a same-repository issue that can admit an external pull request."""

from __future__ import annotations

import json
import os
import re
import sys
from collections.abc import Iterator, Mapping
from typing import Any

CLOSING_REFERENCE = re.compile(
    r'^\s*(?:[-*]\s+)?(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+'
    r'(?:(?P<repository>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+))?'
    r'#(?P<number>[1-9][0-9]*)\b',
    re.IGNORECASE,
)


def _body_references(body: str, repository: str) -> Iterator[int]:
    for line in body.splitlines():
        match = CLOSING_REFERENCE.match(line)
        if match and (
            not match['repository']
            or match['repository'].casefold() == repository.casefold()
        ):
            yield int(match['number'])


def admission_issue(
    pr: Mapping[str, Any], repository: str, default_branch: str
) -> int | None:
    """Return a same-repository issue referenced at the start of a line."""
    body_references = list(_body_references(pr.get('body') or '', repository))
    if not body_references:
        return None

    if pr['baseRefName'] != default_branch:
        return body_references[0]

    linked_numbers = {
        issue['number']
        for issue in pr['closingIssuesReferences']
        if (
            f'{issue["repository"]["owner"]["login"]}/'
            f'{issue["repository"]["name"]}'
        ).casefold()
        == repository.casefold()
    }
    return next(
        (number for number in body_references if number in linked_numbers), None
    )


if __name__ == '__main__':
    pull_request = json.load(sys.stdin)
    number = admission_issue(
        pull_request, os.environ['GH_REPO'], os.environ['DEFAULT_BRANCH']
    )
    if number is not None:
        print(number)
