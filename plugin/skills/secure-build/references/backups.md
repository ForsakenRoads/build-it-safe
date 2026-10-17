# Backups and deleting data

A backup counts only once a restore from it has worked. An agent's word that "backups exist" is not a backup: in July 2025 Replit's agent wrongly said a rollback was impossible, and in April 2026 an agent deleted a database volume together with the backups stored inside it.

## The rules

- **3-2-1:** three copies, on two kinds of storage, one off-site.
- **Backups live outside the thing that can be deleted.** Not in the same volume, account or project as the data.
- **The backup key cannot delete.** Give the backup tool a key limited to one bucket, without delete rights, and keep old versions for a set number of days. A stolen backup key then cannot wipe the history.
- **Encrypt before upload,** with a password you keep in a password manager and on paper.
- **Test restores** on a schedule, with real files, and compare checksums.
- **Deleting is a separate step.** Archive, verify the archive, record it, then delete, and only with the human's go-ahead.

The kit's `BACKUP-PROTOCOL.md` template gives a full recipe with restic and Backblaze B2.

## What you do

- [ ] Never delete data, buckets, volumes, snapshots or backups. Ask the human.
- [ ] Never claim a backup exists or works unless you have seen a restore succeed in this session.
- [ ] Never give a backup tool a key that can delete, and never store its password in the repository.
- [ ] Before a risky migration, ask the human to take and verify a backup first.

## Sources

- The Register on Replit/SaaStr (21 Jul 2025): https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/
- The Register on PocketOS/Railway (27 Apr 2026): https://www.theregister.com/software/2026/04/27/cursor-opus-agent-snuffs-out-startups-production-database/5224442
- Backblaze B2 application key capabilities: https://www.backblaze.com/docs/cloud-storage-application-key-capabilities
- Backblaze B2 lifecycle rules: https://www.backblaze.com/docs/cloud-storage-lifecycle-rules
- restic documentation: https://restic.readthedocs.io/
