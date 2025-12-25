#!/bin/bash

echo "🔑 SSH Public Keys for GitHub"
echo "============================="
echo ""

echo "📋 Account 1: EcommerceMart"
echo "---"
cat ~/.ssh/id_ed25519_ecommercemart.pub
echo "---"
pbcopy < ~/.ssh/id_ed25519_ecommercemart.pub
echo "✅ Copied to clipboard! Add to: https://github.com/settings/keys"
echo ""
read -p "Press Enter to continue to next account..."

echo ""
echo "📋 Account 2: UnboxTheRepy"
echo "---"
cat ~/.ssh/id_ed25519_unboxtherepy.pub
echo "---"
pbcopy < ~/.ssh/id_ed25519_unboxtherepy.pub
echo "✅ Copied to clipboard! Add to: https://github.com/settings/keys"
echo ""
read -p "Press Enter to continue to next account..."

echo ""
echo "📋 Account 3: LangChain"
echo "---"
cat ~/.ssh/id_ed25519_langchain.pub
echo "---"
pbcopy < ~/.ssh/id_ed25519_langchain.pub
echo "✅ Copied to clipboard! Add to: https://github.com/settings/keys"
echo ""

echo "✅ All done! Don't forget to test with:"
echo "   ssh -T git@github.com-ecommercemart"
echo "   ssh -T git@github.com-unboxtherepy"
echo "   ssh -T git@github.com-langchain"



# Troubleshooting
# If you see "Permission denied (publickey)"

# Check if key is loaded:

# bash   ssh-add -l

# Re-add the key:

# bash   ssh-add --apple-use-keychain ~/.ssh/id_ed25519_ecommercemart


# Fix All Your SSH Keys at Once
# bash# Fix all private keys
# chmod 600 ~/.ssh/id_ed25519_*

# # Fix all public keys
# chmod 644 ~/.ssh/id_ed25519_*.pub

# # Fix SSH directory
# chmod 700 ~/.ssh

# # Fix config file if it exists
# chmod 600 ~/.ssh/config