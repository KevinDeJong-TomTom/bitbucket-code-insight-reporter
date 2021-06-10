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

import click
import json


@click.command()
@click.option(
    "--id",
    required=True,
    help="Unique identifier for the report",
)
@click.option(
    "--title",
    required=True,
    help="Humand readable title for the Code Insight report",
)
@click.option(
    "--details",
    help="Additional details to share withing the Code Insight report",
)
@click.option(
    "--reporter",
    help="Reference to the reporter of the Code Insight Report",
)
@click.option(
    "--link",
    help="Link towards an external report",
)
@click.option(
    "--logo-url",
    help="Link towards an image to be shown in the Code Insight report",
)
@click.option(
    "--workspace",
    help="Absolute path towards the root of the repository. This will be stripped from the file paths in the LLVM logging.",
)
@click.option(
    "--output",
    required=True,
    type=click.File("w", encoding="UTF-8", lazy=True, atomic=True),
    help="Path towards the output file",
)
def main(
    id,
    title,
    details,
    reporter,
    link,
    logo_url,
    workspace,
    output,
):
    print(
        """\
================================
BitBucket Code Insight Generator
================================"""
    )

    _data = {
        "id": id,
    }
    if title:
        _data["title"] = title
    if details:
        _data["details"] = details
    if reporter:
        _data["reporter"] = reporter
    if link:
        _data["link"] = link
    if logo_url:
        _data["logo-url"] = logo_url
    if workspace:
        _data["workspace"] = workspace

    print(f"Generating Report: {json.dumps(_data, indent=4, sort_keys=True)}")

    output.write(json.dumps(_data))
    print("============= DONE =============")

    return 0
