# Team 26 AI Game Player Pitch 分镜与台词

目标时长：约 7 分 40 秒，控制在 10 分钟以内。共 6 张主幻灯片，每张可用分步动画形成多个镜头。
讲述者 A：玩家体验与产品；讲述者 B：AI 与工程。可以交换角色。
英文台词可直接排练；时间为剪辑目标，实际以试录为准，短暂停顿和动画已计入。

## 六张幻灯片

| 页 | 标题 | 核心画面 | 对应时间 |
|---|---|---|---|
| 1 | One move changes everything | Team 26、项目名、Quoridor 棋盘、Move / Wall 两个选择 | 0:00–0:40 |
| 2 | A simple goal with difficult choices | 团队简介、游戏目标、玩家需求、参考实现 | 0:40–1:55 |
| 3 | How our AI would decide | MCTS 搜索树、四步循环、Rules / AI / GUI 架构 | 1:55–3:55 |
| 4 | Challenge without the wait | GUI mock-up、难度按钮、测试与评估指标 | 3:55–5:20 |
| 5 | A plan we can deliver | 时间线、四个工作领域、风险与交付物 | 5:20–6:45 |
| 6 | An opponent worth playing | 伦理与素材、所需指导、三项承诺、开场棋盘 | 6:45–7:40 |

## 分镜与英文台词

### 镜头 1｜0:00–0:15｜A｜幻灯片 1

画面：棋盘占画面主体，左上角常驻 Team 26 / AI Game Player。蓝色人类棋子和橙色 AI 棋子；用标签区别，不能只依赖颜色。底部显示 Illustrative position。人物小窗出现在右下角。
动作：高亮一条通往目标边的路线，再出现 Move / Place a wall 两个按钮。停两秒，给观众想一想。

> One move. Two choices. Would you move your pawn closer to the finish, or place a wall to slow your opponent down? Take a second to decide.

剪辑：轻微棋子落下音即可；不需要夸张音乐或真实倒计时。

### 镜头 2｜0:15–0:40｜B｜幻灯片 1

画面：同一局面分成左右两个“假如”分支，分别标 Move 和 Wall。分步画出路径变化；不标胜率，不宣称某一步必胜。

> Moving looks like progress. But a wall can change both players’ routes. The better choice depends on what happens next. That is the challenge behind our proposal: an AI opponent for Quoridor that makes decisions under a time limit, while keeping the game enjoyable for a human player.

过渡：路径动画缩小，变成下一页棋盘缩略图。

### 镜头 3｜0:40–1:00｜A｜幻灯片 2

画面：Team 26 / Proposed game: Quoridor / Human versus MCTS AI。保留棋盘；两个讲述者并排出现一次，其余时间用单人小窗。

> We are Team 26. Our proposal brings together a rules-correct game, a Monte Carlo Tree Search opponent, selectable difficulty, and a clear graphical interface. We would also deliver software design documentation and a user manual, so someone else can understand and run the finished game.

### 镜头 4｜1:00–1:25｜A｜幻灯片 2

画面：Skills → Contribution，最多三行，例如 Rules、AI、GUI and testing。具体技能只能用成员确认过的信息。

> [Insert 40–50 words about the whole team’s confirmed skills and experience. Connect each strength to a project contribution. Suggested structure: “Our experience in … would support … . Members with … could contribute to … . Together, these strengths would help us … .”]

录制前必须替换方括号内容，不能把提示语读进视频。这里概括全队，不只介绍两个讲述者；不需要八个人各录一段。

### 镜头 5｜1:25–1:55｜B｜幻灯片 2

画面：用 Goal → Move or wall → Keep a path 三个短标签讲解。末尾出现 Board Game Arena reference 的小文字链接。

> Quoridor has a clear goal: reach the opposite edge. Each turn offers movement or wall placement, but both players must retain a route to their goal. This creates strategic choices without a real-time interface. Board Game Arena provides a digital reference; our focus would be a documented MCTS opponent with difficulty we can evaluate.

画面注明参考网址：https://boardgamearena.com/gamepanel?game=quoridor 。用自己的棋盘示意，不复制平台截图或标志。本文只把该平台当参考，不宣称其缺少 AI 或难度功能。

### 镜头 6｜1:55–2:30｜B｜幻灯片 3

画面：棋盘缩到左侧，右侧出现两个候选动作及搜索树。循环亮起 Selection → Expansion → Simulation → Backpropagation。少量节点，不做密密麻麻的整棵树。

> So, how would the AI choose? MCTS builds a search tree from the current position. It selects a promising branch, expands a possible move, simulates what might happen, and sends the result back through the tree. Repeating this process helps it balance exploring new options with investigating moves that have performed well so far.

### 镜头 7｜2:30–2:55｜B｜幻灯片 3

画面：两个 rollout 小图，标 Random 和 Route-aware；显示 Move budget，不显示捏造的跑分。角落常驻 Proposed approach。

> We would start with standard MCTS, then compare random rollouts with simple route-aware rollouts. Long simulations would have a cutoff and a documented path-distance estimate. Wall placement creates a large branching factor, so we would profile the search and evaluate candidate filtering if necessary. The underlying game rules would remain unchanged.

### 镜头 8｜2:55–3:25｜A｜幻灯片 3

画面：Rules → AI → GUI 三个模块。墙放下后，如果阻断路径，预览出现无效符号和文字提示；有效墙则保留两条路线。

> The AI needs a reliable game underneath it. Our rules module would handle legal pawn movement, wall conflicts, state transitions, and victory detection. A graph-based check would reject any wall that removes either player’s route to their goal. Separating the rules from search and presentation would let us test these behaviors independently.

### 镜头 9｜3:25–3:55｜B｜幻灯片 3

画面：Java / JavaFX / Maven / JUnit；旁边一条主界面轨道、一条后台 AI 轨道。AI 搜索时界面仍可显示状态。

> We propose Java and JavaFX, with Maven for builds and JUnit for tests. JavaFX suits the board interface and its visual feedback. The AI would search copied game states in a background task with a bounded time budget. That separation should keep the interface responsive and prevent search from modifying the live board.

### 镜头 10｜3:55–4:25｜A｜幻灯片 4

画面：自制 GUI mock-up，标 Proposed interface。依次放大墙预览、合法动作提示、难度按钮。不要伪装成实际运行演示。

> From the player’s perspective, the important questions are simple: what can I do, what just happened, and how difficult is my opponent? Our proposed interface would answer those through legal-move feedback, wall previews, and clear difficulty controls. An unbeatable AI might be impressive. An opponent you enjoy playing against is our goal.

### 镜头 11｜4:25–4:50｜B｜幻灯片 4

画面：Easy / Medium / Hard 三个卡片，下方小字 Initial budgets: 0.2 / 0.5 / 1 s — to be calibrated。不要显示“保证更强”。

> Difficulty would initially use search budgets of point two, point five, and one second. Those are starting values, not proven difficulty levels. We would adjust them using measured playing strength and response time. Giving the AI more time is useful only if the result creates a meaningful and usable difference for the player.

### 镜头 12｜4:50–5:20｜A｜幻灯片 4

画面：三列指标 Win rate / Move latency / Unfinished games；底部小字 Balanced first-player assignments。用检查项替代虚构统计图。

> We would compare difficulty levels and a movement-only shortest-path baseline, initially using one hundred games per matchup with balanced first-player assignments. We would report win rates, response times, and unfinished games separately. Rules and integration tests would cover jumps, blocked paths, wall conflicts, restart, and victory. This would give us evidence to explain our design decisions.

### 镜头 13｜5:20–5:55｜B｜幻灯片 5

画面：Nov 2026 → Dec → Feb 2027 → Apr → May；每个节点只有短标签，页脚标 Provisional milestones — subject to supervisor agreement。

> Our provisional milestones are a playable rules prototype by November, an MCTS baseline by December, difficulty evaluation by February, and an integrated, tested game with documentation by April, ready for the May showcase. We would align these dates with module deadlines and the supervisor’s advice. Each iteration would produce something demonstrable, rather than leaving integration until the end.

这里沿用 EoI 的现有计划，不新增迭代周期或修改里程碑。

### 镜头 14｜5:55–6:20｜A｜幻灯片 5

画面：Rules / AI / GUI / Testing and documentation 四个领域，统一标 Lead + reviewer。下面显示 Weekly meetings / Shared backlog / Reviewed PRs。

> We propose paired ownership across rules, AI, GUI, and testing and documentation, with a lead and reviewer for each area. Assignments would follow the team’s confirmed skills. Weekly meetings, a shared backlog, and reviewed pull requests would help us coordinate work. Design notes and the user manual would develop alongside the software.

### 镜头 15｜6:20–6:45｜B｜幻灯片 5

画面：三个风险依次变成应对：Limited MCTS experience → Early prototype；Slow search → Profile and bound；Integration → Regular review。不朗读整张表。

> The main risks are limited MCTS experience, expensive wall validation, weak rollouts, and integration problems alongside other coursework. We would address these through early prototypes, profiling, bounded search budgets, paired learning, and regular integration. Our priority would be a correct, usable two-player game, before adding optional features.

### 镜头 16｜6:45–7:10｜A｜幻灯片 6

画面：Licensed assets / No accounts required / Accessible controls 三个简短标签；末尾出现 Guidance from supervisor。

> We would check code and asset licenses, avoid unauthorized branding, and design the game without player accounts or personal-data collection. Clear feedback and accessible controls would support usability. Any human playtesting would first be discussed with the supervisor for consent and ethics requirements. We would also welcome guidance on search evaluation and game complexity.

这段所需支持是指导，不新增 EoI 未承诺的数据或设备需求。

### 镜头 17｜7:10–7:40｜B 接 A｜幻灯片 6

画面：回到开场棋局，显示原来的 Move / Wall 选择；随后三项承诺出现 Rules-correct / Responsive / Evaluated。最后两位讲述者并排，停留项目名与 Team 26 两秒。

B:
> Back to our opening question: move, or place a wall? We do not want to guess which AI is better. We want to build an opponent whose decisions, difficulty, and limitations we can test and explain.

A:
> Choose Team 26 for a clear plan: a rules-correct game, a responsive interface, and an evaluated MCTS opponent. Our goal is an opponent that makes you think one move further. Thank you.

## 制作与排练检查

- 英文旁白现有 824 词；填入40–50词团队简介后约864–874词。先按每分钟约120–130词试录，另留约30–45秒给开场思考、动画及转场；预计约7–8分钟，实际时长以试录为准。
- 同一张幻灯片内切换动画与局部放大；6 张主幻灯片足够，避免每个镜头做成新页。
- 所有棋盘布局和动作在录制前按规则复核；开场只展示选择，不断言最优解，不编造棋局结果。
- 搜索树标 Illustrative search；GUI 标 Proposed interface；预算和里程碑标 Provisional。不制作虚假的实际测试结果或运行演示。
- 两个人可以分别录旁白与人物画面后剪辑，接话处留约一秒。人物小窗避开棋盘、图例和字幕；技术动画用全屏更清楚。
- 收音优先：安静环境、稳定音量；字幕核对 Quoridor、MCTS、JavaFX。背景音乐可不用，或只在开头结尾轻放。
- 全片保持一套蓝／橙配色，但同时用文字和形状区别玩家；背景简洁，不用未经许可的公司标志。
- 录前补齐镜头 4 的团队真实技能。这里的分镜是提案演示，最终交付仍需按官方名称导出 MP4。

## 内容依据

依据同目录最新 EoI：team26-UoN-AIGamePlayer-EoI.docx。视频结构、时长和幻灯片数量参考课程 lecture3EOIAndPitchPreparation.pdf 第17–20页。
技术与交付要求对应项目 brief 的游戏、MCTS、难度、GUI、设计文档和用户手册。
