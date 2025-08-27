#!/usr/bin/env python3
"""
Example usage of the standalone GitHub Provider module

This script demonstrates how to use the extracted GitHub provider
for various GitHub operations.
"""

import os
import sys
from github_provider_final import GitHubProvider, get_logger, get_settings

def setup_demo():
    """Setup demo environment"""
    print("🚀 GitHub Provider Standalone Demo")
    print("=" * 50)
    
    # Check for GitHub token
    token = os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_ACCESS_TOKEN')
    if not token:
        print("⚠️  No GitHub token found!")
        print("   Set GITHUB_TOKEN environment variable for full functionality")
        print("   Example: export GITHUB_TOKEN='your_token_here'")
        print()
    else:
        print("✅ GitHub token found")
    
    return token is not None

def demo_basic_functionality():
    """Demonstrate basic provider functionality"""
    print("\n📋 Basic Functionality Demo")
    print("-" * 30)
    
    try:
        # Test basic instantiation
        provider = GitHubProvider()
        print("✅ GitHubProvider instantiated successfully")
        
        # Show configuration
        config = get_settings()
        print(f"✅ GitHub API URL: {config.get('GITHUB.BASE_URL')}")
        print(f"✅ Default model: {config.get('config.model')}")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def demo_pr_analysis(pr_url: str):
    """Demonstrate PR analysis functionality"""
    print(f"\n🔍 PR Analysis Demo")
    print("-" * 30)
    print(f"Analyzing: {pr_url}")
    
    try:
        provider = GitHubProvider(pr_url)
        
        # Basic PR info
        print(f"✅ PR URL: {provider.get_pr_url()}")
        print(f"✅ PR Branch: {provider.get_pr_branch()}")
        
        # Get description
        description = provider.get_pr_description_full()
        if description:
            print(f"✅ Description: {description[:100]}{'...' if len(description) > 100 else ''}")
        else:
            print("ℹ️  No description available")
        
        # Get changed files
        files = provider.get_diff_files()
        print(f"✅ Found {len(files)} changed files")
        
        if files:
            print("\n📁 Changed Files:")
            for i, file in enumerate(files[:5]):  # Show first 5 files
                print(f"   {i+1}. {file.filename}")
                print(f"      Type: {file.edit_type.name}")
                print(f"      Changes: +{file.num_plus_lines} -{file.num_minus_lines} lines")
                if file.language:
                    print(f"      Language: {file.language}")
            
            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more files")
        
        # Get repository languages
        languages = provider.get_languages()
        if languages:
            print(f"\n🌐 Repository Languages:")
            sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            for lang, bytes_count in sorted_langs[:5]:
                percentage = (bytes_count / sum(languages.values())) * 100
                print(f"   {lang}: {percentage:.1f}% ({bytes_count:,} bytes)")
        
        # Get commit messages
        commits = provider.get_commit_messages()
        if commits:
            print(f"\n📝 Recent Commits ({len(commits)}):")
            for i, msg in enumerate(commits[:3]):
                first_line = msg.split('\n')[0] if msg else "Empty commit"
                print(f"   {i+1}. {first_line[:60]}{'...' if len(first_line) > 60 else ''}")
        
        # Get existing comments
        comments = provider.get_issue_comments()
        print(f"\n💬 PR has {len(comments)} comments")
        
        return True
        
    except Exception as e:
        print(f"❌ PR analysis failed: {e}")
        return False

def demo_file_operations():
    """Demonstrate file filtering and language detection"""
    print(f"\n📂 File Operations Demo")
    print("-" * 30)
    
    from github_provider_final import filter_ignored, is_valid_file, set_file_languages, FilePatchInfo, EDIT_TYPE
    
    # Create sample files
    sample_files = [
        FilePatchInfo("src/main.py", "", "", "src/main.py", edit_type=EDIT_TYPE.MODIFIED),
        FilePatchInfo("package-lock.json", "", "", "package-lock.json", edit_type=EDIT_TYPE.MODIFIED),
        FilePatchInfo("README.md", "", "", "README.md", edit_type=EDIT_TYPE.ADDED),
        FilePatchInfo("test.log", "", "", "test.log", edit_type=EDIT_TYPE.ADDED),
        FilePatchInfo("app.js", "", "", "app.js", edit_type=EDIT_TYPE.MODIFIED),
    ]
    
    print("📋 Sample files:")
    for file in sample_files:
        print(f"   - {file.filename}")
    
    # Test file validation
    print("\n✅ File validation:")
    for file in sample_files:
        valid = is_valid_file(file.filename)
        status = "✅ Valid" if valid else "❌ Invalid"
        print(f"   {file.filename}: {status}")
    
    # Test file filtering
    print("\n🔍 After filtering:")
    filtered_files = filter_ignored(sample_files)
    for file in filtered_files:
        print(f"   - {file.filename}")
    
    # Test language detection
    print("\n🌐 With language detection:")
    files_with_lang = set_file_languages(filtered_files)
    for file in files_with_lang:
        lang = getattr(file, 'language', 'Unknown')
        print(f"   - {file.filename}: {lang}")

def demo_configuration():
    """Demonstrate configuration system"""
    print(f"\n⚙️  Configuration Demo")
    print("-" * 30)
    
    config = get_settings()
    
    print("📋 Current configuration:")
    print(f"   GitHub API URL: {config.get('GITHUB.BASE_URL')}")
    print(f"   Verbosity level: {config.get('config.verbosity_level')}")
    print(f"   Max description tokens: {config.get('config.MAX_DESCRIPTION_TOKENS')}")
    print(f"   Default model: {config.get('config.model')}")
    
    print("\n🔧 Language extensions:")
    lang_map = config.get('language_extension_map_org', {})
    for lang, exts in list(lang_map.items())[:5]:
        print(f"   {lang}: {', '.join(exts)}")
    
    print("\n🚫 Bad extensions (first 10):")
    bad_exts = config.get('bad_extensions.default', [])
    print(f"   {', '.join(bad_exts[:10])}")

def demo_logging():
    """Demonstrate logging functionality"""
    print(f"\n📝 Logging Demo")
    print("-" * 30)
    
    logger = get_logger()
    
    print("Testing different log levels:")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.debug("This is a debug message (may not show)")

def interactive_demo():
    """Interactive demo allowing user to input PR URL"""
    print(f"\n🎮 Interactive Demo")
    print("-" * 30)
    
    while True:
        pr_url = input("\nEnter a GitHub PR URL (or 'quit' to exit): ").strip()
        
        if pr_url.lower() in ['quit', 'exit', 'q']:
            break
        
        if not pr_url:
            continue
            
        if 'github.com' not in pr_url or 'pull' not in pr_url:
            print("❌ Please enter a valid GitHub PR URL")
            print("   Example: https://github.com/owner/repo/pull/123")
            continue
        
        success = demo_pr_analysis(pr_url)
        if success:
            print("\n✅ Analysis complete!")
        else:
            print("\n❌ Analysis failed - check the URL and your GitHub token")

def main():
    """Main demo function"""
    # Setup
    has_token = setup_demo()
    
    # Run demos
    demos = [
        ("Basic Functionality", demo_basic_functionality),
        ("File Operations", demo_file_operations),
        ("Configuration", demo_configuration),
        ("Logging", demo_logging),
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"❌ {name} demo failed: {e}")
    
    # PR Analysis demo (if token available)
    if has_token:
        # Try with a public PR
        public_pr = "https://github.com/microsoft/vscode/pull/200000"  # This might not exist
        print(f"\n🔍 Attempting to analyze a public PR...")
        print("(This may fail if the PR doesn't exist or is private)")
        
        try:
            demo_pr_analysis(public_pr)
        except Exception as e:
            print(f"❌ Public PR analysis failed: {e}")
            print("This is expected if the PR doesn't exist")
    
    # Interactive demo
    if has_token:
        try:
            interactive_demo()
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted by user")
    else:
        print(f"\n💡 Set GITHUB_TOKEN to try the interactive PR analysis demo")
    
    print(f"\n🎉 Demo complete!")
    print("📖 See README_github_provider.md for more information")

if __name__ == "__main__":
    main()

