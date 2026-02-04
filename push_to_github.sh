#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Push Secret Scanner to GitHub                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🔐 Enter your GitHub Personal Access Token:"
read -s GITHUB_TOKEN
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ No token provided"
    exit 1
fi

# Create repository using Python
python3 << EOF
from github import Github
import sys

try:
    g = Github("${GITHUB_TOKEN}")
    user = g.get_user()
    print(f"✓ Authenticated as: {user.login}")
    
    # Try to create repository
    print("\n📦 Creating repository 'secret-scanner'...")
    try:
        repo = user.create_repo(
            name="secret-scanner",
            description="Production-grade secret detection tool for Git repositories and GitHub projects",
            private=False,
            auto_init=False,
            has_issues=True,
            has_wiki=True,
            has_projects=True
        )
        print(f"✓ Repository created: {repo.html_url}")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("💡 Repository already exists, using it...")
            repo = user.get_repo("secret-scanner")
            print(f"✓ Using repository: {repo.html_url}")
        else:
            raise e
    
    # Save username for git commands
    with open('/tmp/github_user.txt', 'w') as f:
        f.write(user.login)
    
    print("\n✅ Repository ready!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "Failed to create repository"
    exit 1
fi

# Get username
GITHUB_USER=$(cat /tmp/github_user.txt)

echo ""
echo "🔄 Configuring git remote..."

# Remove existing remote if any
git remote remove origin 2>/dev/null || true

# Add remote with token authentication
git remote add origin https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/secret-scanner.git

echo "✓ Remote configured"
echo ""
echo "📤 Pushing to GitHub..."

# Push to main branch
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                 🎉 SUCCESS!                                 ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Your repository is live at:"
    echo "🔗 https://github.com/${GITHUB_USER}/secret-scanner"
    echo ""
    echo "Clone with:"
    echo "   git clone https://github.com/${GITHUB_USER}/secret-scanner.git"
else
    echo "❌ Push failed. Please check the error above."
    exit 1
fi
