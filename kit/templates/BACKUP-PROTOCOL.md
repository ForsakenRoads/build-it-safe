# Backup protocol: restic + Backblaze B2

This is a general recipe for an encrypted, off-site backup that a stolen key cannot wipe. It uses **restic** (free, open-source backup software that encrypts on your machine) and **Backblaze B2** (pay-as-you-go cloud storage). The same ideas work with other tools and providers.

Facts below were checked against the restic and Backblaze documentation as of October 2026. Prices and features change; check the links.

## The rules this protocol follows

1. **3-2-1:** three copies of your data, on two kinds of storage, one of them off-site. This protocol is the off-site copy; you still need a local one, such as an external disk.
2. **Encrypted before it leaves your machine,** with a password only you hold.
3. **The backup key cannot delete.** If someone steals it, they can add files but cannot erase your history.
4. **Old versions are kept for a set time** (here 30 days), so a mistake or an attack can be undone.
5. **No standing restore key.** You create a read-only key only when you need to restore.
6. **Tested.** A backup counts only once you have restored from it.
7. **AI agents never get backup credentials,** and never run backup or restore commands.

## Step 1. Install restic from the official release

- Use a current release (0.19.1 as of October 2026). Releases come with SHA-256 sums and a GPG signature; check them. https://github.com/restic/restic/releases
- Version 0.15.0 or later is needed for keys without delete rights: restic then "hides" files instead of deleting them (restic changelog, enhancement #2134).
- Many Linux distributions ship an older restic; prefer the official release.

## Step 2. Create the bucket

In the Backblaze web console:
- Create a **private** bucket.
- Turn on **server-side encryption** (SSE-B2). restic already encrypts; this is a second layer.
- Add a **lifecycle rule** that keeps prior versions for 30 days ("Keep prior versions for this number of days"). In B2 terms this sets `daysFromHidingToDeleting` to 30. Hidden versions "are still available for download using their specific file ID" until then, and they count toward your storage bill.
- Turn on two-factor authentication for your Backblaze account, and save the recovery codes.

## Step 3. Create one key, limited to that bucket, without delete rights

The console's "Read and Write" preset includes `deleteFiles`, so create the key with Backblaze's command-line tool or API instead, choosing the capabilities yourself:

```
listBuckets, listFiles, readFiles, writeFiles
```

Restrict it to the one bucket. A bucket-restricted key "can only act on its assigned bucket". Never give the backup key `deleteFiles`, `writeKeys` (which grants "full access to the account") or `bypassGovernance`.

restic's own documentation now recommends B2's **S3-compatible API** over the native B2 backend, because of error-handling issues in the B2 library it uses. Create the key as above and follow restic's "Amazon S3" instructions with your bucket's S3 endpoint.

## Step 4. Store the secrets where agents cannot read them

- The **repository password** encrypts everything. Generate a long random one, show it once, save it in a password manager **and** on paper kept away from the computer. If you lose it, the backup cannot be opened by anyone, including you.
- The **key ID and key** go in a file readable only by the account that runs the backup, for example a root-owned file with mode `0600`, loaded only by the backup script.
- Run backups from a separate account (such as root via a system timer), not from the account where your AI agents run. Agents run as you; if they cannot read the file, a prompt-injected agent cannot leak it.
- Run privileged backup commands yourself, in your own terminal, never through an agent.
- If the password or key is ever pasted into a chat, an issue or a log, rotate it.

## Step 5. Choose what to back up

Include: your projects, documents, configuration (`/etc` on Linux), and a list of installed packages.

Exclude what you can recreate:
- dependency folders (`node_modules`, virtual environments), build output, caches;
- folders marked with a `CACHEDIR.TAG` file (restic's `--exclude-caches` skips them);
- **login tokens and API keys**: after a disaster you sign in again and make new keys instead of restoring old ones.

Use `--one-file-system` so a mounted network drive is not swept in by accident. If a source lives on an external drive, check that it is mounted before each backup, so an unplugged drive is a loud failure and never an empty snapshot.

## Step 6. Schedule it

- **Daily backup.** Use a timer that catches up after the machine was off (on Linux, a systemd timer with `Persistent=true`).
- **Weekly `restic check`.**
- **Monthly `restic check --read-data-subset=1/12`**, a different twelfth each month, so the whole repository is read once a year.
- Run at low priority so it does not slow you down.

## Step 7. Watch it

- Have the backup write a status file (last success, last failure).
- Alert when a run fails, when there has been no success for 36 hours, or when the weekly check is late.
- Do not let a known, harmless failure hide new real ones.
- Add an alert that does not depend on the machine itself (a "dead-man switch" service that warns when your backup stops checking in).

## Step 8. Test restores

- At least monthly, restore a random sample of real files to a temporary folder and compare SHA-256 checksums with the originals.
- Write a short `RECOVERY.md`: how to install restic on a new machine, create a temporary **read-only** key (`listBuckets, listFiles, readFiles`), and restore. Print it and keep it with the password sheet.

## Step 9. Pruning and deleting

- Do not prune (`restic forget --prune`) automatically at first. When you add it, keep a generous policy (for example 14 daily, 8 weekly, 12 monthly) and protect snapshots you tag as archives (`--keep-tag archive`).
- Pruning needs delete rights. Use a separate, temporary key for it, by hand.
- Before deleting any local data because "it is in the backup": take a snapshot, verify that the files are in it, record that, and only then delete, as a separate step.

## Optional: an Object Lock vault

Backblaze **Object Lock** makes files impossible to change or delete until a date you choose.
- **Governance mode:** retention "can be modified or overridden by clients with appropriate app key capabilities" (`bypassGovernance`).
- **Compliance mode:** retention "cannot be removed by any user".
- Object Lock can be turned on for new or existing buckets, but "after you enable Object Lock on a bucket, you cannot disable this setting", and you pay for locked storage until the date passes.

A second bucket with Object Lock in Governance mode, a short retention period and no key that holds `bypassGovernance`, protects against an attacker who gets past everything above. Start without it; add it once the basic protocol has run for a few months.

## Sources

- restic documentation, preparing a repository (Backblaze B2 and S3): https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html
- restic changelog, enhancement #2134 (B2 keys without delete rights): https://github.com/restic/restic/blob/master/CHANGELOG.md
- restic releases: https://github.com/restic/restic/releases
- Backblaze, application key capabilities: https://www.backblaze.com/docs/cloud-storage-application-key-capabilities
- Backblaze, lifecycle rules: https://www.backblaze.com/docs/cloud-storage-lifecycle-rules
- Backblaze, Object Lock: https://www.backblaze.com/docs/cloud-storage-object-lock
- Cache directory tags: https://bford.info/cachedir/
