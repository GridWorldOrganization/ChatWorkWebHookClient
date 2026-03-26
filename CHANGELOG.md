# Changelog

## [0.1.0] - 2026-03-26

### Added
- `/system` command: system-wide status display (OS, AI mode, SQS, Google API, members)
- `/bill` command: monthly Anthropic API usage and estimated cost tracking
- `/gws` command: Google Workspace API connection test (CRUD test with temp spreadsheet)
- `/talk` command: view/change conversation mode per room (mode 0-4)
- Conversation mode 4: "Rebellion mode" (contrarian persona responses)
- Google Workspace URL auto-detection: Sheets/Docs/Slides/Drive URLs in messages are fetched and included in AI prompts
- Google Workspace API integration via OAuth (replaces service account approach)
- `USE_DIRECT_API` option: switch between Claude Code CLI (default) and Anthropic API direct call
- API usage tracking with token count recording (`api_usage.json`)
- `SQS_WAIT_TIME_SECONDS` for short/long polling switch
- Window close (X button) cleanup via `SetConsoleCtrlHandler`
- `atexit` cleanup as fallback
- `kill_zombie.bat`: zombie process detection and cleanup tool (`--all` for extended mode)
- `check_gws.bat` / `check_gws.py`: Google Workspace API connection checker
- `check_claude_task.bat`: Native/npm Claude process detection
- Multi-instance prevention in `start_poller.bat` (auto-kill zombie + restart)
- ChatWork API timeout (30s) on all 7 API call sites
- Casual chat filter for mode 0 (skip greetings without AI call)
- `DEBUG_NOTICE_ENABLED` flag for debug notification on/off
- Startup API connectivity test for debug notification room
- CLI mode: PID startup/shutdown logging with `proc.poll()` verification
- Startup log: `where claude` result showing Native/npm and full path
- `docs/` folder: architecture.md, commands.md

### Changed
- Default `USE_DIRECT_API` changed from `1` to `0` (Claude Code CLI is now default)
- Renamed `CHATWORK_API_TOKEN_ERROR_REPORTER` → `DEBUG_NOTICE_CHATWORK_TOKEN`
- Renamed `CHATWORK_ERROR_ROOM_ID` → `DEBUG_NOTICE_CHATWORK_ROOM_ID`
- Removed `MAINTENANCE_ROOM_ID` (all commands now use `DEBUG_NOTICE_CHATWORK_ROOM_ID`)
- Conversation mode 0 renamed from "Maintenance" to "Log"
- All commands restricted to `DEBUG_NOTICE_CHATWORK_ROOM_ID` only
- README.md restructured: technical details moved to `docs/`
- QUICKSTART.md updated to reflect all changes
- Google API scopes unified into single constant (`GOOGLE_API_SCOPES`)
- Added `presentations.readonly` scope for Google Slides support

### Fixed
- Self-messages not deleted from SQS in `process_member_batch` (zombie message loop)
- `/talk` `/gws` commands executable from unauthorized rooms (moved after whitelist check)
- Sheets API range `Sheet1!A1:B2` fails in Japanese locale (changed to `A1:B2`)
- `setup_windows.bat` AWS key skip message causing batch syntax error (Japanese in if-block)
- Google API scope inconsistency between token creation and usage

## [0.1.0] - 2026-03-25

### Added
- Initial release
- SQS polling with batch processing
- Multi-member parallel execution
- Conversation modes (0-3)
- Room-specific settings
- AI-to-AI conversation with turn limit
- Follow-up auto-reply
- `/status` `/session` maintenance commands
- Graceful shutdown (Ctrl+C)
- Room whitelist
