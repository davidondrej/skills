---
name: push-skill-to-github
description: Commit and push agent-skill changes to the user's private skills GitHub repo (rooted at ~/.agents). Use after creating or updating any skill, when the user says "push the skill", "push skills to github", "save the skill to my repo", or "update the skills repo". Handles staging, committing, pushing, and cleaning up the cmux pane used to do it.
---

# Push Skills to GitHub

For committing any skill change to the user's private skills repo, git root **`~/.agents`** (this is also the canonical skill folder; `.claude` and `.pi/agent/skills` symlink to `~/.agents/skills`). Pushes here auto-publish a sanitized public mirror to `davidondrej/skills` — never push directly to that public repo.

Use this after creating or editing a skill. If the skill is distributed to all agents, do that first (`distribute-skill-to-all-agents`), then run this to push the canonical copy.

## Steps

**Not in cmux?** (no `$CMUX_WORKSPACE_ID`): skip the cmux pane steps — just run the git commands from step 2 directly in any available terminal, then verify the push output.

1. **Open a fresh cmux pane** in the current workspace, no focus steal:
   ```bash
   cmux new-pane --type terminal --direction right --workspace "$CMUX_WORKSPACE_ID" --focus false
   cmux list-panes --workspace "$CMUX_WORKSPACE_ID"   # note the NEW pane + its surface ref
   ```
2. **Stage, commit, push** in `~/.agents` (send to the new pane's surface):
   ```bash
   cmux send --surface surface:NEW 'cd ~/.agents && git add -A && git commit -m "<concise message>" && git push'
   cmux send-key --surface surface:NEW enter
   ```
3. **Verify** the push landed:
   ```bash
   sleep 2
   cmux read-screen --surface surface:NEW | tail -15   # expect "main -> main"
   ```
4. **Close the pane** once confirmed:
   ```bash
   cmux close-surface --surface surface:NEW
   cmux list-panes --workspace "$CMUX_WORKSPACE_ID"    # confirm the pane is gone
   ```

## Notes
- Always run git from `~/.agents` (the repo root), not `~/.agents/skills`.
- Write a concise, specific commit message describing the skill change.
- Only push to GitHub when the user asks. Don't push speculatively.
