## Your connection {#ch-connection}

::: {.dek}
A VPN moves your trust from the network to a company. Choose the company carefully, and know what it cannot do.
:::

### The mental model: a private tunnel to someone else's door

A **VPN** (virtual private network) builds an encrypted tunnel from your device to a server run by the VPN company. Your traffic leaves the tunnel there and goes on to the website. So the café's Wi-Fi and your internet provider see only that you are talking to the VPN. The VPN company, in turn, can see where your traffic goes. The digital-rights group EFF puts it this way: the traffic is hidden from your provider, but "it's all visible to the VPN provider" [[eff-vpn]].

A VPN does not remove trust. It moves it, from the network you happen to be on to a company you choose. That is why the choice of company matters more than any feature list.

### When a VPN helps, and when it does not

A VPN **helps** when:

- you use a network you do not trust, such as a café or hotel, and you do not want it to see which sites you visit;
- you do not want the websites you visit to see your home's internet address.

A VPN **does not**:

- **make you anonymous.** EFF: "A VPN is not a tool for anonymity." Sites can still recognize you through logins, cookies and other tracking [[eff-vpn]].
- **protect a hacked account.** If someone has your password or a stolen token, they log in as you, VPN or not. That is what {{ch:ch-accounts}} is for.
- **replace HTTPS.** HTTPS, the padlock in your browser, already encrypts the content of your traffic to each site. EFF notes that it protects "the content of your communications, not the metadata", such as which sites you visit; that metadata is what a VPN can hide from the local network [[eff-vpn]]. Your own site still needs HTTPS ({{ch:ch-websites}}).
- **stop malware or phishing.** A fake login page is just as fake through a tunnel.

EFF also notes that, because most web traffic is now encrypted, using a VPN on public Wi-Fi "isn't as necessary for everyone anymore" [[eff-vpn]]. Use one for a reason, not by default.

### How to judge a VPN: seven questions

1. **Independent audit.** Has an outside security firm examined the servers and the no-logs promise, and published its report?
2. **Court or raid test.** Has the company been ordered by a court, or searched by police, and had no user data to hand over?
3. **Open source.** Can anyone read the code of the apps you install?
4. **Jurisdiction.** In which country is the company based, and what do its laws require it to record or hand over?
5. **Ownership.** Who owns it? Is the owner known and stable, with no history of selling user data?
6. **Technical design.** Do the servers keep no data on disk, or encrypt their disks fully? Does it use a modern protocol such as WireGuard? Does it have a "kill switch" that blocks traffic if the tunnel drops? Does it leak your real address through DNS (the internet's address book), IPv6 or the browser's WebRTC feature?
7. **Anonymous sign-up.** Can you sign up and pay without giving your name or email address?

**WireGuard** is "an extremely simple yet fast and modern VPN that utilizes state-of-the-art cryptography" [[wireguard-home]]. Most good providers now offer it.

### Two providers with published evidence, as of October 2026

Every fact below comes from the company's own pages, an auditor's report or press coverage, checked in October 2026. Companies change; check again before you buy. No company paid to be listed, and there are no referral links.

| Question | Mullvad VPN | Proton VPN |
|---|-----------|-----------|
| Independent audit | Cure53 tested its VPN server infrastructure in June 2024 and called it "generally in exemplary condition" [[cure53-mullvad-2024]]. In January 2026, X41 D-Sec reviewed its account, payment and key-distribution services, found five issues, none giving access to user data, and judged its API to have a "high security level" [[x41-mullvad-2026; mullvad-x41-2026]]. In March 2026, Assured found "no major vulnerabilities" in GotaTun, its new WireGuard implementation [[mullvad-gotatun-audit]] | Securitum has audited its no-logs policy every year from 2022 to 2026, and found no evidence that the reviewed servers log user activity [[proton-nologs-audit]] |
| Court or raid test | Swedish police searched its office on 18 April 2023 to seize customer data; they "left without taking anything and without any customer information" [[mullvad-raid-2023]] | Proton says its VPN no-logs policy has been "tested in over 400 legal cases" [[proton-nologs-audit]] (Proton's own figure) |
| Open-source apps | Yes, under the GPL-3.0 license [[mullvad-app-repo]] | Proton says all its apps are open source [[proton-nologs-audit]] |
| Jurisdiction | Sweden: the company is based in Gothenburg [[mullvad-about]] | Switzerland. In 2025, citing a proposed change to Swiss surveillance rules, Proton said it would move some of its physical infrastructure out of the country, starting with its AI assistant; it says it is "not performing a gradual exit from Switzerland" [[cyberinsider-proton-swiss]] |
| Ownership | Owned by its two founders through its parent company, Amagicom AB [[mullvad-about]] | Its non-profit Proton Foundation is the "primary shareholder" [[proton-foundation]] |
| Servers | "All of our VPN servers run from RAM, with no persistent storage" [[mullvad-servers]] | Disks with full-disk encryption, keys "stored off-site"; Proton argues RAM-only servers add nothing over that [[proton-ram-only]] |
| Protocol | WireGuard only, since OpenVPN was removed in January 2026 [[mullvad-openvpn-removal]] | WireGuard, plus Stealth, its own protocol that disguises VPN traffic for networks that block VPNs [[proton-wireguard; proton-stealth]] |
| Sign-up and price | An account number, no email; cash or crypto accepted; €5 per month [[mullvad-pricing]] | Sign-up asks for an email address: an existing one, or a free @proton.me address [[proton-signup]]. Pay by card, PayPal or Proton credits (credits can be bought with cash or Bitcoin); a free plan. VPN Plus on a two-year plan: $3.49 a month on the pricing page, and a $2.99 offer on the sign-up page, both on 16 October 2026 [[proton-pricing; proton-signup]] |

The two differ in style. Mullvad asks for the least information about you. Proton offers a free plan and a larger suite of services. As of October 2026, both had published evidence for audits, legal tests, open-source apps, ownership and server design. The table does not cover kill switches or leak tests, and only Mullvad lets you sign up without an email address; check those yourself. Other providers may meet the bar too: apply the questions yourself.

### Reaching your own machines and agents

The more common need for builders is not hiding your browsing. It is reaching your own server, home computer or AI agent from somewhere else. The OpenClaw story in {{ch:ch-openclaw}} shows the wrong way: putting the control panel on a public address. There are two right ways.

**An SSH tunnel.** **SSH** is the standard tool for logging in to another computer securely. It can also carry one connection through its encrypted link. OpenClaw's documentation shows the pattern [[openclaw-remote]]:

```
ssh -N -L 18789:127.0.0.1:18789 user@gateway-host
```

Line by line: `ssh` starts a secure connection. `-N` means "do not open a command line, just carry traffic" [[openssh-manual]]. `-L 18789:127.0.0.1:18789` means "forward connections to port 18789 on *this* computer to port 18789 on the *remote* computer's own loopback address" [[openssh-manual]]. A **port** is a numbered door on a computer; **loopback** (`127.0.0.1`) means "only this computer". `user@gateway-host` is your login on the remote machine. While the command runs, you open `http://127.0.0.1:18789` in your browser, and you reach the dashboard through the tunnel. Nobody else on the internet can.

**A mesh VPN.** A mesh VPN connects your own devices to each other in a private network, wherever they are. Tailscale, for example, "creates a peer-to-peer mesh network", using WireGuard [[tailscale-what]]. OpenClaw's documentation calls loopback plus an SSH tunnel or Tailscale Serve "the safest default (no public exposure)" [[openclaw-remote]].

![Two ways to reach a dashboard. Exposed: anyone on the internet can find the login page. Tunnelled: the dashboard listens only on its own machine, and you reach it through SSH or a private mesh network.](images/diagrams/remote-access.svg){width=95%}

### Common AI-assistant mistakes

- Telling a program to listen on all network addresses (`0.0.0.0`) "so you can reach it from your phone". That also lets everyone else reach it.
- Opening a port on your router or cloud firewall instead of using a tunnel.
- Recommending a VPN as the fix for a security problem it cannot solve, such as a leaked key.

::: {.box .do-this}
**Do this**

- Use a VPN on networks you do not trust, chosen with the seven questions.
- Do not expect a VPN to make you anonymous or to protect your accounts.
- Keep every dashboard and admin page on loopback, and reach it through an SSH tunnel or a mesh VPN.
- Check what your server exposes: list its open ports, or look it up on a search engine such as Censys.
:::
