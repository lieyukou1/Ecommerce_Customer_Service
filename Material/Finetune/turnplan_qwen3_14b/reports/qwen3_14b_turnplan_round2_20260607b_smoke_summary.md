# Track Smoke - qwen3_14b_turnplan_round2_20260607b_smoke

| id | track | json_like | too_short | hard_tone | refusal_like |
| --- | --- | --- | --- | --- | --- |
| clarify_c1 | clarify | False | False | False | False |
| clarify_c2 | clarify | False | False | False | False |
| clarify_c3 | clarify | False | False | False | False |
| clarify_c4 | clarify | False | False | False | False |
| knowledge_k1 | knowledge | False | False | False | False |
| knowledge_k2 | knowledge | False | False | False | False |
| knowledge_k3 | knowledge | False | False | False | False |
| knowledge_k4 | knowledge | False | False | False | False |
| knowledge_k5 | knowledge | False | False | False | False |
| knowledge_k6 | knowledge | False | False | False | False |
| chitchat_h1 | chitchat | False | False | False | False |
| chitchat_h2 | chitchat | False | False | False | False |
| chitchat_h3 | chitchat | False | False | False | False |
| chitchat_h4 | chitchat | False | False | False | False |
| chitchat_h5 | chitchat | False | False | False | False |

## Outputs

### clarify_c1 (clarify)
- user: 我这边有个门禁的事想处理一下
- notes: cold-start ambiguous business request
- reply: 你是想先处理门禁的问题，还是先咨询相关信息呢？

### clarify_c2 (clarify)
- user: 这个我得怎么弄
- notes: focused service item but user direction still fuzzy
- reply: 你想了解这个服务的收费、办理方式、服务说明，还是当前可预约状态呢？

### clarify_c3 (clarify)
- user: 嗯，你继续
- notes: active urge flow still missing reason
- reply: 可以，我先帮你记下，这边再补充一下催办原因会更方便处理。

### clarify_c4 (clarify)
- user: 停车费这块我想先问一下
- notes: longer context after exit should not keep old runtime wording
- reply: 你是想咨询停车费相关规则吗？

### knowledge_k1 (knowledge)
- user: 装修报备一般都得注意什么
- notes: cold-start rule question
- reply: 装修报备一般需要确认装修时间、施工内容、施工人员信息，以及小区要求的材料。建议提前准备好房号、联系人和施工范围等信息，以便顺利办理。具体要求可参考小区最新公告或物业通知。

### knowledge_k2 (knowledge)
- user: 物业费到底是怎么收的，我先搞明白
- notes: spoken fee explanation
- reply: 物业费通常是根据小区公示的收费标准、您的房屋面积以及收费周期来计算的。具体金额和缴费方式，您可以查看最新的物业账单或前往物业收费页面核实。如有疑问，也欢迎随时咨询物业客服。

### knowledge_k3 (knowledge)
- user: 那材料是谁出
- notes: focused service item follow-up
- reply: 关于净水器滤芯更换，我先帮你整理一下：
收费是 149 元；当前状态是“可预约”。
你可以继续问收费、办理方式、服务说明，或者换一个项目继续问。

### knowledge_k4 (knowledge)
- user: 停车这块你也顺便给我讲讲
- notes: longer context topic switch but still knowledge
- reply: 停车管理主要涉及车位类型、月租或临停收费、可停放时段，以及是否需要提前登记车牌。具体收费和规则建议您查看小区最新公告或咨询物业前台。如需办理停车业务，可提供车辆信息和停放需求，我帮您进一步确认。

### knowledge_k5 (knowledge)
- user: 你们平时都能帮住户处理哪些事
- notes: service capabilities overview
- reply: 我们能协助处理的事情包括收费查询、报修服务、投诉反馈、停车管理、装修申请以及社区管理相关事务。您具体想了解哪方面呢？

### knowledge_k6 (knowledge)
- user: 这条之前师傅都看过什么情况
- notes: work order info with focused work order
- reply: 关于工单 WO20260601002，我先帮你看一下：
当前状态是“处理中”。
你可以继续问处理进度、催办、投诉，或者换一条工单继续聊。

### chitchat_h1 (chitchat)
- user: 你好，在吗
- notes: simple greeting
- reply: 在的，有什么可以帮您吗？

### chitchat_h2 (chitchat)
- user: 你是物业客服吗
- notes: identity question
- reply: 我是小区的智能管家，可以陪您聊天，也能协助处理物业相关问题。

### chitchat_h3 (chitchat)
- user: 今天真是被这些事折腾烦了
- notes: light emotion should not force clarify
- reply: 能理解您的心情，需要我帮您处理点什么吗？

### chitchat_h4 (chitchat)
- user: 你平时是不是挺忙的
- notes: probing small talk
- reply: 我这边主要是处理物业相关的事情，有需要可以随时找我。

### chitchat_h5 (chitchat)
- user: 行，那我先熟悉熟悉你
- notes: after one round of small talk
- reply: 好的，有什么需要帮忙的随时找我。
