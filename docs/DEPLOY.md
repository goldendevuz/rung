# Restore Plan

Run the following command to restore the containers in the exact reverse order they were listed before stopping:

```bash
docker start $(tac /root/backups/rung-d1/running-ids.txt | tr '\n' ' ')
```
