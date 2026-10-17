## When the framework breaks {#ch-react2shell}

::: {.dek}
Sometimes you did nothing wrong. Patch the same day, then rotate.
:::

### What happened

React is a widely used library for building web pages, and Next.js is a popular framework built on it. On 3 December 2025, the React team disclosed a flaw with the highest possible severity score, 10.0 out of 10. "An unauthenticated attacker could craft a malicious HTTP request to any Server Function endpoint that, when deserialized by React, achieves remote code execution on the server" [[react-advisory]]. In plain words: a stranger, without logging in, could send one specially built request and run any command on your server.

The flaw became known as React2Shell (CVE-2025-55182). Vercel said it affected "Next.js versions 15.0.0 through 16.0.6" [[vercel-react2shell]]. Wiz reported that, from 04:00 UTC on 5 December, the monitoring company GreyNoise saw automated attempts to exploit it [[wiz-react2shell]].

Wiz reported that "39% of cloud environments contain instances of Next.js or React in versions vulnerable" to it, and that attackers "establish shells to harvest credentials from environment variables, filesystems, and cloud instance metadata" [[wiz-react2shell]]. Microsoft reported "several hundred machines across a diverse set of organizations compromised", and attempts to steal "OpenAI API keys, Databricks tokens, and Kubernetes service‑account credentials" [[ms-react2shell]].

Vercel shipped a one-line fix, `npx fix-react2shell-next`. It also advised: if your application "was online and unpatched as of December 4th, 2025 at 1:00 PM PT, we strongly encourage you to rotate any secrets it uses, starting with your most critical ones" [[vercel-react2shell]].

### Why it happened, in plain words

::: {.box .plain-words}
**Plain words**

- **Framework:** the large body of ready-made code your app is built on, such as Next.js, React, SvelteKit or Django. Your own code is a small layer on top.
- **Remote code execution:** a flaw that lets someone far away run commands on your machine. It is the most serious kind.
- **Patch:** an update that fixes a flaw.
:::

The flaw was in React's own server code, in the part that unpacks data arriving from the internet. The developers of affected apps did not have to make any mistake. React warned: "Even if your app does not implement any React Server Function endpoints it may still be vulnerable if your app supports React Server Components" [[react-advisory]].

Once attackers could run commands on a server, they went straight for the secrets. Every key your app uses sits in its environment variables, so an attacker on the server can read them all. That is why the advice was not only "update", but also "rotate": a patch closes the door, but it does not take back keys that were already copied.

Frameworks are large and complex, and a flaw like this can happen again. The defense is not to avoid frameworks. It is to be ready to update quickly, and to know which keys to change.

::: {.box .lesson}
**The lesson**

- Watch for security notices from your framework and your host. Follow their accounts or mailing lists.
- When a critical advisory appears, patch the same day ({{ch:ch-dependencies}}).
- If your app was exposed before you patched, assume its keys were read. Rotate them, most important first ({{ch:ch-leak}}).
- Keep a short list of every key your app uses and where it is stored, so rotation takes minutes, not days ({{ch:ch-secrets}}).
:::
