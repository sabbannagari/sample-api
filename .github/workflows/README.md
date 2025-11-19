# GitHub Actions Workflow Setup

## Sync with Centralized Repository

This workflow automatically checks out a centralized repository and retrieves changes when push, commit, or merge events occur.

### Configuration Steps

1. **Update the workflow file** (`.github/workflows/sync-centralized-repo.yml`):

   Replace the following placeholders:
   - `OWNER/CENTRALIZED-REPO-NAME` with your actual centralized repository (e.g., `myorg/central-config`)

2. **Create a GitHub Personal Access Token (PAT)**:

   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Give it a descriptive name (e.g., "Centralized Repo Access")
   - Select scopes:
     - ✅ `repo` (Full control of private repositories)
   - Click "Generate token"
   - **Copy the token immediately** (you won't see it again)

3. **Add the token as a repository secret**:

   - Go to your repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `CENTRALIZED_REPO_TOKEN`
   - Value: Paste your Personal Access Token
   - Click "Add secret"

### Workflow Triggers

The workflow triggers on:
- **Push events** to any branch (commits, direct pushes)
- **Pull request merged** to main branch

You can customize the branches by modifying the `on` section in the workflow file.

### What the Workflow Does

1. Checks out your current repository
2. Checks out the centralized repository
3. Displays information about both repositories
4. Shows recent changes from the centralized repo
5. Optionally copies files from centralized repo to current repo
6. Creates a summary of the sync operation

### Customization

#### To copy specific files from centralized repo:

Uncomment and modify the "Copy specific files" step:

```yaml
- name: Copy specific files from centralized repo
  run: |
    cp centralized-repo/config.yml ./config.yml
    cp -r centralized-repo/shared-configs ./
```

#### To commit changes back to your repo:

Add this step at the end:

```yaml
- name: Commit and push changes
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add .
    git diff --quiet && git diff --staged --quiet || git commit -m "Sync from centralized repo"
    git push
```

#### To trigger on specific branches only:

Modify the `on.push.branches` section:

```yaml
on:
  push:
    branches:
      - main
      - develop
      # Remove '**' to limit to specific branches
```

### Testing

Push a commit to your repository and check the Actions tab to see the workflow run.
