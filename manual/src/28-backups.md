## Backups {#ch-backups}

::: {.dek}
A backup counts only if it is elsewhere, cannot be deleted by mistake or malice, and has been restored.
:::

### The mental model: three tests

Many people have something they call a backup that would not save them. A copy is a real backup only if it passes three tests:

1. **It is somewhere else.** A copy on the same disk, or in the same account, dies with the original. PocketOS's backups lived inside the database volume that was deleted ({{ch:ch-least-privilege}}).
2. **Nobody can delete it in a hurry:** not you on a bad day, not your AI agent, and not an attacker who has your laptop's keys. A **mirror**, a copy kept identical to the original, fails this test: when you delete a file, the mirror deletes it too.
3. **You have restored from it.** Until you have brought files back and checked them, you do not know whether it works. Replit's agent said a rollback was impossible; it was wrong, and only trying showed it ({{ch:ch-replit}}).

The classic rule of thumb is **3-2-1**. Backblaze, a cloud storage company, defines it as keeping "three copies of your data on two different media with one copy off-site" [[backblaze-321]].

![The backup protocol in one picture: your computer encrypts the backup, a key that can write but not delete uploads it, the provider keeps deleted versions for a set number of days, and you test restores.](images/diagrams/backup-protocol.svg){width=95%}

### The protocol

This protocol uses two tools. **restic** is free, open-source backup software that encrypts everything on your computer before it leaves [[restic-design]]. **Backblaze B2** is a cloud storage service that stores the encrypted result. The same ideas work with other storage providers.

**1. Install restic from its official release.** Use a current version (0.19.1 was the latest release as of October 2026) [[restic-changelog]]. The "no-delete key" in step 3 needs restic 0.15.0 or later [[restic-changelog]]. Check the download's signature or checksum, as the release page explains.

**2. Create a private bucket.** A **bucket** is a named storage container in your B2 account. Make it private. Turn on two-factor sign-in for your Backblaze account and save the recovery codes.

**3. Create a key that can write but not delete.** B2 **application keys** can be limited to one bucket and to a list of **capabilities**, the actions the key may perform [[b2-app-keys]]. Leave out `deleteFiles`. With restic's own B2 backend (a repository address that starts with `b2:`), restic then "automatically falls back to hiding files" instead of deleting them, which "can prevent an attacker from deleting backups with such an API key" [[restic-changelog]]. Restic's documentation now suggests B2's S3-compatible connection instead [[restic-prepare]]. If you use that, test that your no-delete key still lets backups run and cannot delete a file, before you rely on it. With Backblaze's command-line tool, the command looks like this [[b2-key-create; restic-changelog]]:

```
b2 key create --bucket my-backups backup-writer listBuckets,listFiles,readFiles,writeFiles
```

Line by line: `b2 key create` makes a new application key. `--bucket my-backups` limits it to that one bucket (use your bucket's name). `backup-writer` is a label for the key. The last part is the list of capabilities: list buckets, list files, read files and write files, with no delete. The tool shows the new key once; restic's documentation notes that an application key "will only appear once" [[restic-prepare]]. Store it straight away (step 6).

Check the key's capabilities in the Backblaze web console afterwards. If `deleteFiles` appears, delete the key and start again.

**4. Keep hidden versions for a set time.** When restic works with a key that cannot delete, it can only *hide* files: a hidden file stays stored and can be brought back. A **lifecycle rule** decides when hidden files are really deleted, using a setting called `daysFromHidingToDeleting` [[b2-lifecycle]]. Set it to 30 days, for example. That gives you 30 days to notice a stolen key or a bad clean-up and undo it. Longer windows cost more, because hidden files still count as stored data [[b2-lifecycle]].

**5. Optional: lock a second copy.** B2's **Object Lock** "lets you make data immutable by preventing a file from being changed or deleted until a given date". In *governance* mode, keys with special capabilities can still override the lock; in *compliance* mode, no user can remove it. Once switched on for a bucket, Object Lock cannot be switched off. Backblaze charges nothing extra for it, beyond normal storage [[b2-object-lock]]. Use it for a second, rarely touched copy, and give no everyday key the power to override it.

**6. Protect the password like the data itself.** Restic encrypts your backup with a password. Its documentation warns: "Losing your password means that your data is irrecoverably lost" [[restic-prepare]]. Generate a long password, store it in your password manager, and keep a printed copy somewhere safe away from your computer. Never paste it into a chat. If it is ever exposed, change it with restic's `key passwd` command [[restic-encryption]]. A new password does not change the key that encrypts the data. If someone may also have copied the backup itself, start a new repository with a new password and back up again [[restic-design]].

**7. Keep the backup's secrets away from your agents.** Put the B2 key and the password in files that only the backup's own system account can read, and run the backup as that account. Your AI agents run as you, so they cannot read those files. Never give an agent these keys or administrator rights, and run any administrator commands yourself, in your own terminal.

**8. Choose what to back up.** Back up your projects, your settings and your documents. Leave out what you can download or rebuild: caches, installed dependencies and build output. Restic's `--exclude-caches` option skips any folder that holds a standard `CACHEDIR.TAG` marker file [[restic-backup]]. Leave out login tokens and API keys too: after a disaster, sign in again and make new ones, instead of restoring old keys from a backup.

**9. Run it on a schedule, and check it.** Back up daily. Run `restic check` weekly; it checks that the repository is consistent [[restic-working]]. Once a month, run `restic check --read-data-subset=1/12`, then `2/12` the next month, and so on: each run reads one twelfth of the stored data, so in a year every byte has been read back once [[restic-working]].

**10. Practice restoring.** Every month, restore a handful of random files to a temporary folder and compare them with the originals. Write a one-page recovery sheet: where the backup is, which account, where the password is kept, and the restore commands. Print it and store it with the paper password. Do not keep a standing "restore key"; at disaster time, create a read-only key just for the restore.

**11. Make failures loud.** A backup that stops silently is worse than none, because you still trust it. Have the schedule alert you when a backup or check fails, or when no backup has succeeded for more than a day. If you back up an external drive, check that it is actually connected first, so an unplugged drive is a loud failure, not an empty backup.

**12. Delete old backups only on purpose.** Restic's `forget` and `prune` commands remove old snapshots. They need a key that *can* delete, so keep that work separate: a separate key, used by hand, rarely. When you do clean up, protect snapshots you must keep with `--keep-tag` [[restic-forget]].

### Common AI-assistant mistakes

- Suggesting a "Read and Write" key without checking whether it includes delete rights.
- Setting up a sync tool, such as a mirror, and calling it a backup.
- Storing the backup password or key in the project, or printing it in the setup log.
- Reporting that "backups are configured" without a restore test.

::: {.box .do-this}
**Do this**

- Keep at least one copy off-site, with a key that cannot delete it.
- Keep deleted versions for a set number of days (a lifecycle rule), or lock a second copy.
- Store the backup password in your password manager and on paper. Never give it to an agent.
- Check the backup weekly, and read all of it back over a year.
- Restore real files every month, and keep a printed recovery sheet.
:::
