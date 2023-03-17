"""Page Level Rules and Definitions."""

# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

from typing import Dict, Any, Union
from resources.types import Page, LintStats, Resource

from rules.logger import RulesLogger

class PageRules:
    """Page Level Rules and Definitions."""
    def __init__(
            self,
            console,
            disable_map: Dict[str, Any]):

        self.console = console
        self.disable_map = disable_map
        self.log = RulesLogger(console=console)

    def check_and_log_naming(
        self,
        page: Page,
        stats: LintStats,
        res: Union[re.Match, None],
        pattern: str):
        """Checks for final naming match and calls logger."""
        rule = "R015: Naming Conventions"

        if not res:
            resource = Resource()
            resource.agent_id = page.agent_id
            resource.flow_display_name = page.flow.display_name
            resource.flow_id = page.flow.resource_id
            resource.page_display_name = page.display_name
            resource.page_id = page.resource_id
            resource.resource_type = "page"

            message = ": Page Display Name does not meet the specified"\
                f" Convention : {pattern}"
            
            stats.total_issues += 1

            self.log.generic_logger(resource, rule, message)

        return stats

    # naming-conventions
    def page_naming_conventions(
        self, page: Page, stats: LintStats) -> LintStats:
        """Check that the Page Display Name conform to naming conventions."""

        # Return early if Start Page
        if page.display_name == 'Start Page':
            return stats

        # Form Pages
        if page.form and page.naming_pattern_form:
            pattern = page.naming_pattern_form
            res = re.search(pattern, page.display_name)
            stats.total_inspected += 1
            
            stats = self.check_and_log_naming(page, stats, res, pattern)

        # Webhook Pages
        elif page.has_webhook and page.naming_pattern_webhook:
            pattern = page.naming_pattern_webhook
            res = re.search(pattern, page.display_name)
            stats.total_inspected += 1
            
            stats = self.check_and_log_naming(page, stats, res, pattern)

        # Generic Pages
        elif page.naming_pattern_generic:
            pattern = page.naming_pattern_generic
            res = re.search(pattern, page.display_name)
            stats.total_inspected += 1
            
            stats = self.check_and_log_naming(page, stats, res, pattern)

        return stats

    # missing-webhook-event-handlers
    def missing_webhook_event_handlers(
        self, page: Page, stats: LintStats) -> LintStats:
        """Checks for missing Event Handlers on pages that use Webhooks."""
        rule = "R011: Missing Webhook Event Handlers"

        stats.total_inspected += 1

        if page.has_webhook and not page.has_webhook_event_handler:
            resource = Resource()
            resource.agent_id = page.agent_id
            resource.flow_display_name = page.flow.display_name
            resource.flow_id = page.flow.resource_id
            resource.page_display_name = page.display_name
            resource.page_id = page.resource_id
            resource.resource_type = "page"

            message = ""

            stats.total_issues += 1
            self.log.generic_logger(resource, rule, message)

        return stats

    def run_page_rules(self, page: Page, stats: LintStats):
        """Checks and Executes all Page level rules."""
        # naming-conventions
        if self.disable_map.get("naming-conventions", True):
            stats = self.page_naming_conventions(page, stats)

        # missing-webhook-event-handlers
        if self.disable_map.get("missing-webhook-event-handlers", True):
            stats = self.missing_webhook_event_handlers(page, stats)

        return stats
