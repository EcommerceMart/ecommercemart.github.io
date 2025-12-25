#!/bin/bash

echo "🔑 GitHub Multiple Accounts SSH Setup"
echo "======================================"
echo ""

# Account details
ACCOUNT1="ecommercemart"
EMAIL1="your_ecommercemart_email@example.com"

ACCOUNT2="unboxtherepy"
EMAIL2="your_unboxtherepy_email@example.com"

ACCOUNT3="langchain"
EMAIL3="your_langchain_email@example.com"

echo "📝 Step 1: Generating SSH keys..."
echo ""

# Generate keys
ssh-keygen -t ed25519 -C "$EMAIL1" -f ~/.ssh/id_ed25519_$ACCOUNT1 -N ""
ssh-keygen -t ed25519 -C "$EMAIL2" -f ~/.ssh/id_ed25519_$ACCOUNT2 -N ""
ssh-keygen -t ed25519 -C "$EMAIL3" -f ~/.ssh/id_ed25519_$ACCOUNT3 -N ""

echo "✅ SSH keys generated!"
echo ""

echo "📝 Step 2: Adding keys to SSH agent..."
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/id_ed25519_$ACCOUNT1
ssh-add --apple-use-keychain ~/.ssh/id_ed25519_$ACCOUNT2
ssh-add --apple-use-keychain ~/.ssh/id_ed25519_$ACCOUNT3

echo "✅ Keys added to agent!"
echo ""

echo "📝 Step 3: Creating SSH config..."
cat > ~/.ssh/config << EOF
# Account 1: $ACCOUNT1
Host github.com-$ACCOUNT1
    HostName github.com
    User git
    AddKeysToAgent yes
    UseKeychain yes
    IdentityFile ~/.ssh/id_ed25519_$ACCOUNT1

# Account 2: $ACCOUNT2
Host github.com-$ACCOUNT2
    HostName github.com
    User git
    AddKeysToAgent yes
    UseKeychain yes
    IdentityFile ~/.ssh/id_ed25519_$ACCOUNT2

# Account 3: $ACCOUNT3
Host github.com-$ACCOUNT3
    HostName github.com
    User git
    AddKeysToAgent yes
    UseKeychain yes
    IdentityFile ~/.ssh/id_ed25519_$ACCOUNT3
EOF

echo "✅ SSH config created!"
echo ""

echo "🔑 PUBLIC KEYS TO ADD TO GITHUB:"
echo "================================="
echo ""

echo "📋 ACCOUNT 1: $ACCOUNT1"
echo "Copy this key and add to https://github.com/settings/keys"
echo "---"
cat ~/.ssh/id_ed25519_$ACCOUNT1.pub
echo "---"
pbcopy < ~/.ssh/id_ed25519_$ACCOUNT1.pub
echo "✅ Copied to clipboard!"
echo ""
read -p "Press Enter after adding key to GitHub..."

echo ""
echo "📋 ACCOUNT 2: $ACCOUNT2"
echo "Sign out and sign in to $ACCOUNT2, then add to https://github.com/settings/keys"
echo "---"
cat ~/.ssh/id_ed25519_$ACCOUNT2.pub
echo "---"
pbcopy < ~/.ssh/id_ed25519_$ACCOUNT2.pub
echo "✅ Copied to clipboard!"
echo ""
read -p "Press Enter after adding key to GitHub..."

echo ""
echo "📋 ACCOUNT 3: $ACCOUNT3"
echo "Sign out and sign in to $ACCOUNT3, then add to https://github.com/settings/keys"
echo "---"
cat ~/.ssh/id_ed25519_$ACCOUNT3.pub
echo "---"
pbcopy < ~/.ssh/id_ed25519_$ACCOUNT3.pub
echo "✅ Copied to clipboard!"
echo ""
read -p "Press Enter after adding key to GitHub..."

echo ""
echo "🧪 Testing connections..."
echo ""

echo "Testing $ACCOUNT1..."
ssh -T git@github.com-$ACCOUNT1

echo ""
echo "Testing $ACCOUNT2..."
ssh -T git@github.com-$ACCOUNT2

echo ""
echo "Testing $ACCOUNT3..."
ssh -T git@github.com-$ACCOUNT3

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update your repository remotes:"
echo "   git remote set-url origin git@github.com-$ACCOUNT1:USERNAME/repo.git"
echo ""
echo "2. Configure Git user per repository:"
echo "   git config user.name 'Your Name'"
echo "   git config user.email 'your@email.com'"