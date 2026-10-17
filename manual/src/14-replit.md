## The agent with the keys to production {#ch-replit}

::: {.dek}
An instruction in chat is not a lock.
:::

### What happened

In July 2025 Jason Lemkin, the founder of SaaStr, a large community for software businesses, ran a public experiment. He built an app with Replit's AI agent and posted about it every day. An AI agent is an AI that does not just suggest code: it runs commands, edits files and changes systems on its own.

On 18 July he posted that Replit "goes rogue during a code freeze and shutdown and deletes our entire database" [[x-lemkin-deleted]]. A code freeze is a period when nobody is supposed to change anything. Lemkin said he had "explicitly told it eleven times in ALL CAPS not to do this" [[register-replit]]. He also reported that the agent had been "creating fake data, fake reports", including "a 4,000-record database full of fictional people" [[register-replit]].

The agent told him that a rollback, which means restoring the earlier version, was "impossible in this case". That was wrong. Lemkin later reported that "the rollback did work" [[register-replit]]. Fortune reported that the deleted data covered "more than 1,200 executives" and "over 1,190 companies" [[fortune-replit]]. Lemkin also reported "$607.70 in additional charges beyond my $25/month Core plan" [[register-replit]].

On 20 July, Replit's CEO Amjad Masad posted: "Replit agent in development deleted data from the production database. Unacceptable and should never be possible." He said Replit was rolling out automatic separation of development and production databases, and was "actively working on a planning/chat-only mode so you can strategize without risking your codebase" [[x-masad-replit; fortune-replit]].

Lemkin's posts are his own account on social media, but Replit's CEO confirmed the central fact: the agent deleted production data.

### Why it happened, in plain words

::: {.box .plain-words}
**Plain words**

- **Production:** the real, live system that your users use, with their real data.
- **Development:** a copy where you build and test. Breaking it should cost nothing.
:::

The agent could run destructive commands against the live database. Nothing in the system stopped it. Lemkin had told it, in capital letters, many times, not to touch anything. But a sentence in a chat is a request. The agent reads it, weighs it against everything else it has read, and can still decide to act. Only a real limit stops an action every time: a database account that cannot delete, a development copy that is separate from production, or a setting the agent cannot change.

The story also shows a second problem. The agent reported things that were not true: fake data, and a rollback that "could not" work. An AI agent's description of what it did is not evidence. You need to check the result yourself.

::: {.box .lesson}
**The lesson**

- Keep AI agents away from production. Give them a development database and development keys only ({{ch:ch-least-privilege}}; {{ch:ch-agent}}).
- Put hard limits in settings and permissions, not in chat. Rules in chat help; they do not stop anything.
- Take backups that the agent cannot reach, and test that they restore ({{ch:ch-backups}}).
- Check what the agent says it did. Look at the data, the bill and the test results yourself.
:::
