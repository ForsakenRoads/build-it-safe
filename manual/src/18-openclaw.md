## Agents left on the open internet {#ch-openclaw}

::: {.dek}
An agent that holds your keys needs a locked door, not a public address.
:::

### What happened

OpenClaw (first called Clawdbot, then Moltbot) is an open-source personal AI agent. You run it on your own computer or a rented server, connect it to your accounts and chat apps, and it acts for you. It went viral in January 2026.

Many people made its control panel reachable from the whole internet. Censys, a company that maps what is exposed online, wrote that "as of 31 January 2026, Censys has identified 21,639 exposed instances", up "from around 1,000 instances to over 21,000 in under a week" [[censys-openclaw]]. Censys added an important qualifier: "Most deployed instances seen by Censys are accessible, however, still require a token value" to view and use them [[censys-openclaw]]. So most were reachable but still locked. A security researcher reported finding hundreds of panels that exposed API keys, bot tokens and chat histories; that report comes from social media and trade press, and is unconfirmed [[trending-openclaw]].

At the same time, attackers went after OpenClaw's add-ons, which it calls "skills". The security company Koi Security audited 2,857 skills on ClawHub, OpenClaw's skill store, and found 341 malicious ones. 335 of them used fake setup steps to install a password-stealing program for Macs, Atomic Stealer [[thn-clawhub]].

### Why it happened, in plain words

::: {.box .plain-words}
**Plain words**

- **Control panel (dashboard):** a web page for managing a program. For an agent, it can show its chats, its connected accounts and its keys.
- **Exposed to the internet:** reachable by anyone who knows or finds its address. Search engines like Censys find such addresses automatically.
- **Skill:** an add-on that teaches an agent a new task. It is software from a stranger, even when it looks like a short text file.
:::

A personal agent is powerful because it holds your keys and accounts. That also makes its control panel one of the most valuable things you own. Putting it on a public address means that its login screen, if it has one, is the only thing between every stranger on the internet and your accounts.

OpenClaw's own documentation recommends the safe pattern. It says: "Keep the Gateway **loopback-only** unless you are sure you need a bind." Loopback means the program listens only to the computer it runs on. To reach it from elsewhere, the documentation shows an SSH tunnel, and calls loopback plus an SSH tunnel or Tailscale Serve "the safest default (no public exposure)" [[openclaw-remote]]. {{Ch:ch-connection}} explains both tools.

The skills problem is older than AI. App stores and package registries have always attracted malware. What is new is how much an agent's add-on can do once installed: it runs with the agent's access to everything.

::: {.box .lesson}
**The lesson**

- Never expose an agent's dashboard, or any admin page, to the internet. Reach it through an SSH tunnel or a private mesh network ({{ch:ch-connection}}).
- If something must be public, put a strong login in front of it, and check what search engines like Censys can see.
- Treat agent skills, plugins and MCP servers as software from strangers. Read them before you install them ({{ch:ch-agent}}).
:::
