# DGP-Bot
Automation bot for DGP-Studio GitHub management

## BOT Issue 检查任务
- 检查是否拥有一个合适的标题
  - 若未设置标题则 close as not planned
  - 若 close 后修改标题则 reopen
- 检查 Windows 版本是否达到最低要求/是否为过时的版本
- 检查胡桃版本号是否为最新
- 当有设备 ID 时获取用户日志并发布
- 根据用户选择的问题分类添加对应的 tag
- 当 issue 被打上 `BUG` 或 `Feat` 标签时，添加进 Project 的备忘录环节
- 当有 commit 被 push，检查该 commit 是否关闭 issue
  - 若需要关闭 issue 则添加 `已修复` 和 `等待发布` 标签并留言
  - 当有正式版 release 发布时，删除全部 `等待发布` 标签并留言