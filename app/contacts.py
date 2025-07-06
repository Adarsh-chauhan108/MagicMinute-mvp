# [file name]: contacts.py
import json
from memory_manager import MemoryManager
from llm_interpreter import interpret_task_with_llm

memory = MemoryManager()

def resolve_email(name_or_email):
    """Resolves a name to email using the MemoryManager"""
    if "@" in name_or_email:
        return name_or_email
    
    # Check memory first
    email = memory.get_contact(name_or_email.lower())
    if email:
        return email
    
    # Fallback to legacy contacts.json if exists
    try:
        with open("contacts.json", "r") as f:
            contacts = json.load(f)
        return contacts.get(name_or_email)
    except:
        return None
    
def test_contact_commands():
    """Test various contact saving commands"""
    print("🧪 Testing Contact Commands\n" + "="*50)
    
    test_commands = [
        "save chauhanadarsh101@gmail.com as Adarsh",
        "save john.doe@company.com as John Doe",
        "save sarah@example.org as Sarah",
        "save invalid-email as Test",  # Should fail
        "save test@email.com as",      # Should fail - no name
        "show contacts",
        "list contacts"
    ]
    
    for cmd in test_commands:
        print(f"\n📝 Command: '{cmd}'")
        result = interpret_task_with_llm(cmd)
        print(f"✅ Response: {result.get('markdown_response', 'No response')}")
        print("-" * 40)

def test_signature_commands():
    """Test various signature saving commands"""
    print("\n🖊️ Testing Signature Commands\n" + "="*50)
    
    test_commands = [
        "save Ayush as signature",
        "call me Ayush Kumar",
        "my name is Ravi",
        "set signature to Priya",
        "set signature as Amit",
        "show signature",
        "current signature"
    ]
    
    for cmd in test_commands:
        print(f"\n📝 Command: '{cmd}'")
        result = interpret_task_with_llm(cmd)
        print(f"✅ Response: {result.get('markdown_response', 'No response')}")
        print("-" * 40)

def test_email_with_contacts():
    """Test email composition using saved contacts"""
    print("\n📧 Testing Email with Contacts\n" + "="*50)
    
    # First save some contacts
    print("Setting up test contacts...")
    interpret_task_with_llm("save test@example.com as TestUser")
    interpret_task_with_llm("save ayush@email.com as Ayush")
    interpret_task_with_llm("save Ayush Kumar as signature")
    
    test_commands = [
        "send email to TestUser about project update",
        "compose email to Ayush regarding meeting tomorrow",
        "draft email to test@example.com about vacation plans"
    ]
    
    for cmd in test_commands:
        print(f"\n📝 Command: '{cmd}'")
        result = interpret_task_with_llm(cmd)
        print(f"✅ Task Type: {result.get('task_type')}")
        print(f"📧 To: {result.get('recipient')}")
        print(f"📋 Subject: {result.get('subject')}")
        if result.get('contact_resolved'):
            print(f"🔗 Contact Resolution: {result['contact_resolved']}")
        print("-" * 40)

if __name__ == "__main__":
    print("🚀 MagicMinute Contact & Signature Testing")
    print("=" * 60)
    
    try:
        test_contact_commands()
        test_signature_commands() 
        test_email_with_contacts()
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("Make sure your environment is set up correctly with:")
        print("- OpenAI API key in .env file")
        print("- memory_manager.py is working")
        print("- All dependencies are installed")