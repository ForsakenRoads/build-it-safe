## Websites {#ch-websites}

::: {.dek}
A few settings tell every visitor's browser how to protect them. They are free.
:::

### The mental model: instructions you send with every page

When your server sends a page, it sends a few lines of instructions with it, called **headers**. The visitor never sees them, but the browser obeys them. Some headers tell the browser to protect the visitor: "only ever talk to this site over an encrypted connection", or "only run scripts that come from these places". Without them, the browser falls back on more trusting defaults.

These settings will not fix a broken lock on your database. They protect your visitors from a different family of attacks: someone between them and you on the network, a script injected into your page, or a fake page that wraps yours.

### HTTPS everywhere

**HTTPS** encrypts the connection between the visitor's browser and your site, so nobody on the network can read or change what passes between them. The padlock in the address bar shows it. HTTPS needs a **certificate**, a file that proves your site is really yours. Certificates are free: Let's Encrypt is "a free, automated, and open Certificate Authority" run by a nonprofit [[letsencrypt-about]]. Most hosting services set up HTTPS for you; check that yours has, for every address your site uses.

### Four headers worth knowing

- **Strict-Transport-Security (HSTS)** "informs browsers that the host should only be accessed using HTTPS, and that any future attempts to access it using HTTP should automatically be upgraded to HTTPS" [[mdn-hsts]]. It stops anyone from quietly downgrading a visitor to an unencrypted connection.
- **Content-Security-Policy (CSP)** "allows website administrators to control resources the user agent is allowed to load for a given page" [[mdn-csp]]. In plain words, it lists where scripts, styles and images may come from. If an attacker manages to slip a script into your page, the browser refuses to run it, because it is not on the list.
- **`frame-ancestors`**, part of CSP, "specifies valid parents that may embed a page" [[mdn-csp]]. Set it so that only your own site can embed your pages. That stops **clickjacking**: a fake site that shows your page inside its own, invisibly, and tricks visitors into clicking your buttons.
- **X-Content-Type-Options: nosniff** tells the browser to trust the file type your server declares, and not to guess it [[mdn-nosniff]]. That stops an uploaded file from being run as a script.

You set these in your host's or framework's configuration. Your AI assistant can write them for you; ask it to explain each one, then test the result.

### Free checkers

- **Mozilla's HTTP Observatory**, at `developer.mozilla.org/en-US/observatory`, "performs an in-depth assessment of a site's HTTP headers and other key security configurations" [[mdn-observatory]]. It moved to MDN on 2 July 2024 [[mdn-observatory-faq]]. Note that "the scan history for each domain is public" [[mdn-observatory-faq]].
- Your browser's own developer tools show the headers of any page: open them, choose the Network tab, reload, and click the first request.

Run a check before launch, and again after any change to your hosting setup.

### Common AI-assistant mistakes

- Writing a content security policy that allows everything (`*` or `unsafe-inline` everywhere) to make an error go away. It removes the protection.
- Setting headers on some pages and not on others, such as API routes or error pages.
- Turning off certificate checks (`--insecure`, `rejectUnauthorized: false`) to get past an error during development, and leaving it in.

::: {.box .do-this}
**Do this**

- Serve every address of your site over HTTPS, and send the HSTS header.
- Add a content security policy, starting strict, and loosen it only for sources you name.
- Set `frame-ancestors` and `X-Content-Type-Options: nosniff`.
- Check your site with the HTTP Observatory before launch.
- Search your code for disabled certificate checks, and remove them.
:::
