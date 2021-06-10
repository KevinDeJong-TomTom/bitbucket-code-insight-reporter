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

import requests


class Bitbucket:
    def __init__(self, url, username, password):
        self._auth = (username, password)
        self._url = url

    def _report_url(self, project_key, repository_slug, commit_id, report_key):
        return (
            self._url
            + "/rest/insights/1.0/projects/"
            + project_key
            + "/repos/"
            + repository_slug
            + "/commits/"
            + commit_id
            + "/reports/"
            + report_key
        )

    def _annotations_url(self, project_key, repository_slug, commit_id, report_key):
        return (
            self._url
            + "/rest/insights/1.0/projects/"
            + project_key
            + "/repos/"
            + repository_slug
            + "/commits/"
            + commit_id
            + "/reports/"
            + report_key
            + "/annotations"
        )

    def delete_code_insights_report(
        self, project_key, repository_slug, commit_id, report_key
    ):
        val = requests.delete(
            self._report_url(project_key, repository_slug, commit_id, report_key),
            auth=self._auth,
        )

    def create_code_insights_report(
        self, project_key, repository_slug, commit_id, report_key, **report
    ):
        requests.put(
            self._report_url(project_key, repository_slug, commit_id, report_key),
            json=report,
            auth=self._auth,
        )

    def add_code_insights_annotations_to_report(
        self, project_key, repository_slug, commit_id, report_key, annotations
    ):
        requests.post(
            self._annotations_url(project_key, repository_slug, commit_id, report_key),
            json={"annotations": annotations},
            auth=self._auth,
        )
