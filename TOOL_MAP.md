# Canonical tool map

Generated from core/tools.py. Prompt name, schema identifier and dispatcher key are identical. Security policy runs outside the model tool registry.

| Planner / registry identifier | Executor function | Permitted agent | Parameters |
|---|---|---|---|
| list_directory | agents.os_agent.list_directory | os_agent | path |
| read_file | agents.os_agent.read_file | os_agent | path |
| delete_file | agents.os_agent.delete_file | os_agent | path |
| create_folder | agents.os_agent.create_folder | os_agent | path |
| write_file | agents.os_agent.write_file | os_agent | path, content |
| copy_file | agents.os_agent.copy_file | os_agent | source, destination |
| move_file | agents.os_agent.move_file | os_agent | source, destination |
| verify_file | agents.os_agent.verify_file | os_agent | path, expected_content (optional) |
| open_application | agents.os_agent.open_application | os_agent | app_name, window_title |
| type_in_window | agents.os_agent.type_in_window | os_agent | window_title, text |
| read_ui_tree | agents.os_agent.read_ui_tree | os_agent | window_title |
| click_ui_element | agents.os_agent.click_ui_element | os_agent | window_title, element_name, expected_element |
| verify_window | agents.os_agent.verify_window | os_agent | window_title, expected_text (optional) |
| navigate_and_read | agents.browser_agent.navigate_and_read | browser_agent | url |
| browser_click | agents.browser_agent.click_element | browser_agent | url, selector, expected_selector |
| browser_fill | agents.browser_agent.fill_element | browser_agent | url, selector, text |
| send_message | agents.comm_agent.send_message | comm_agent | app_name, contact, text, recipient_control_name, search_bar_name (optional), message_box_name (optional) |
| read_latest_message | agents.comm_agent.read_latest_message | comm_agent | app_name |
| search_files_by_name | agents.research_agent.search_files_by_name | research_agent | directory, pattern |
| search_files_by_content | agents.research_agent.search_files_by_content | research_agent | directory, query, extension (optional) |
| vision_locate_element | agents.vision_agent.vision_locate_element | vision_agent | window_title, element_description |
| capture_screenshot | agents.vision_agent.capture_screenshot | vision_agent | output_path |

Text data parameters content/text/expected_content/query also accept an explicit earlier-step reference at the plan layer, resolved and revalidated before dispatch. See WORKFLOW_CONTRACTS.md. Recipient headers must equal contact, contact plus ` (You)`, or contact plus ` (You) Message yourself`; arbitrary unrelated controls are rejected. Browser state is scoped to one pipeline task. Tool count remains 22.
