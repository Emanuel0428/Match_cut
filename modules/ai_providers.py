# AI Provider Modules
import os

# --- AI Provider Imports ---
MISTRAL_AVAILABLE = False
GEMINI_AVAILABLE = False
ANTHROPIC_AVAILABLE = False
DEEPSEEK_AVAILABLE = False

try:
    from mistralai import UserMessage, SystemMessage, Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    print("Mistral AI library not found. Install with: pip install mistralai")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    print("Google Gemini library not found. Install with: pip install google-generativeai")

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    print("Anthropic library not found. Install with: pip install anthropic")

try:
    from deepseek import DeepSeek
    DEEPSEEK_AVAILABLE = True
except ImportError:
    print("DeepSeek library not found. Install with: pip install deepseek")

def initialize_ai_client(provider, api_key):
    """Initialize the appropriate AI client based on provider."""
    if not api_key:
        return None

    try:
        if provider == 'mistral' and MISTRAL_AVAILABLE:
            return Mistral(api_key=api_key)
        elif provider == 'gemini' and GEMINI_AVAILABLE:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('gemini-pro')
        elif provider == 'anthropic' and ANTHROPIC_AVAILABLE:
            return Anthropic(api_key=api_key)
        elif provider == 'deepseek' and DEEPSEEK_AVAILABLE:
            return DeepSeek(api_key=api_key)
    except Exception as e:
        print(f"Error initializing {provider} client: {e}")
        return None
    
    return None

def create_prompt_for_provider(provider, target_lines, min_lines, highlighted_text):
    """Creates an appropriate prompt for each AI provider."""
    base_prompt = (
        f"Task: Generate exactly {target_lines} lines of coherent, natural text in a single language (no more, no less).\n\n"
        f"Rules:\n"
        f"1. Each line MUST be a complete, meaningful sentence in natural language\n"
        f"2. One line MUST contain exactly this phrase: '{highlighted_text}'\n"
        f"3. IMPORTANT: Each line MUST be 50-80 characters long (no short lines)\n"
        f"4. Create a coherent paragraph where all lines relate to each other\n"
        f"5. The text should flow naturally with the highlighted phrase integrated seamlessly\n"
        f"6. Write in a descriptive, engaging style that makes sense to a human reader\n"
        f"7. Every line must be substantial and meaningful, not just filler text\n"
        f"8. Fill all available space with properly formatted lines of text\n\n"
        f"Format:\n"
        f"- Return ONLY the lines of text\n"
        f"- Separate lines with single newlines\n"
        f"- No numbering, no quotes, no extra formatting\n"
        f"- EVERY line must be a complete sentence with proper punctuation\n\n"
    )

    if provider == 'anthropic':
        return f"You are a creative writer. {base_prompt}"
    elif provider == 'gemini':
        return f"You are a text generation expert. {base_prompt}"
    else:
        return base_prompt

def generate_mistral_text(client, model, prompt, highlighted_text):
    """Generate text using Mistral AI."""
    messages = [
        SystemMessage(content="You are a text generation assistant that creates natural, coherent text. Follow formatting rules exactly and create meaningful sentences that flow naturally."),
        UserMessage(content=prompt)
    ]
    response = client.chat.complete(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=800
    )
    return process_ai_response(response.choices[0].message.content, highlighted_text)

def generate_gemini_text(client, prompt, highlighted_text):
    """Generate text using Google Gemini."""
    response = client.generate_content(prompt)
    return process_ai_response(response.text, highlighted_text)

def generate_anthropic_text(client, prompt, highlighted_text):
    """Generate text using Anthropic Claude."""
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=800,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}]
    )
    return process_ai_response(response.content[0].text, highlighted_text)

def generate_deepseek_text(client, prompt, highlighted_text):
    """Generate text using DeepSeek."""
    response = client.generate_text(prompt)
    return process_ai_response(response, highlighted_text)

def process_ai_response(content, highlighted_text):
    """Process AI response and extract lines and highlight index."""
    # Clean up the content by removing any markdown formatting or extra spaces
    cleaned_content = content.replace('```', '').replace('**', '').strip()
    
    # Split into lines and clean each line
    lines = [line.strip() for line in cleaned_content.split('\n') if line.strip()]
    
    # Filter out any lines that might be instructions or formatting
    filtered_lines = []
    for line in lines:
        # Skip lines that look like instructions or headings
        if line.startswith('#') or line.startswith('-') or line.startswith('*') or \
           line.startswith('Note:') or line.startswith('Format:'):
            continue
        # Skip numbered lines (like "1. ", "2. ")
        if len(line) > 2 and line[0].isdigit() and line[1] == '.' and line[2] == ' ':
            line = line[3:]
        filtered_lines.append(line)
    
    # Find highlight line
    highlight_index = -1
    for i, line in enumerate(filtered_lines):
        if highlighted_text in line:
            highlight_index = i
            break
    
    # Ensure we have enough lines by duplicating if necessary
    MIN_REQUIRED_LINES = 12  # Ensure we have at least this many lines
    
    if len(filtered_lines) < MIN_REQUIRED_LINES:
        # Add duplicate lines with small modifications to reach minimum count
        original_line_count = len(filtered_lines)
        
        for i in range(MIN_REQUIRED_LINES - original_line_count):
            # Select a line to duplicate (avoiding the highlight line)
            source_idx = (i % original_line_count)
            if source_idx == highlight_index and original_line_count > 1:
                source_idx = (source_idx + 1) % original_line_count
            
            source_line = filtered_lines[source_idx]
            
            # Make a small modification to the line
            words = source_line.split()
            if len(words) > 3:
                # Change an adjective or swap word order
                filtered_lines.append(" ".join(words[::-1]).capitalize() + ".")
            else:
                # Just append the original if it's too short to modify
                filtered_lines.append(source_line)
    
    return filtered_lines, highlight_index

def generate_ai_text_snippet(client, provider, model, highlighted_text, min_lines, max_lines):
    """Generates text using the specified AI provider with improved reliability."""
    if not client:
        return None, -1

    # Always request maximum lines to ensure proper screen filling
    target_lines = max_lines
    prompt = create_prompt_for_provider(provider, target_lines, min_lines, highlighted_text)

    # Add more specific instructions based on provider to enhance quality
    if provider == 'anthropic':
        # Anthropic Claude responds well to more structured prompts
        prompt += (
            "\nThis text will be used for a video effect, so it's important that:\n"
            "1. The text reads naturally and coherently\n"
            "2. All sentences connect logically to each other\n"
            "3. The highlighted phrase is integrated seamlessly\n"
            "4. No placeholder text, lorem ipsum, or gibberish is used"
        )
    elif provider == 'mistral':
        # Mistral benefits from clear formatting expectations
        prompt += (
            "\nPlease generate text that reads naturally. No gibberish, placeholder text, or random characters."
        )

    try:
        lines = None
        highlight_index = -1
        
        # Provider-specific generation
        if provider == 'mistral':
            lines, highlight_index = generate_mistral_text(client, model, prompt, highlighted_text)
        elif provider == 'gemini':
            lines, highlight_index = generate_gemini_text(client, prompt, highlighted_text)
        elif provider == 'anthropic':
            lines, highlight_index = generate_anthropic_text(client, prompt, highlighted_text)
        elif provider == 'deepseek':
            lines, highlight_index = generate_deepseek_text(client, prompt, highlighted_text)
            
        # Validate the generated text
        if lines and highlight_index != -1:
            # Check each line for minimum quality standards
            valid_lines = []
            for line in lines:
                # Filter out any non-sentence content, headers, code blocks, etc.
                if (len(line) >= 40 and  # Stricter minimum length (was 15)
                    len(line) <= 100 and  # Maximum length
                    ' ' in line and  # Contains spaces (not just a token)
                    ('.' in line or '?' in line or '!' in line) and  # Has proper punctuation
                    not line.startswith('#') and  # Not a markdown header
                    not line.startswith('```') and  # Not a code block
                    not line.startswith('---') and  # Not a separator
                    line.strip() and  # Not just whitespace
                    len(line.split()) >= 5):  # At least 5 words
                    
                    # Add valid line
                    valid_lines.append(line)
            
            # If we have valid lines, return them
            if valid_lines and len(valid_lines) >= min_lines:
                # Recalculate highlight index in case lines were filtered
                new_highlight_index = -1
                for i, line in enumerate(valid_lines):
                    if highlighted_text in line:
                        new_highlight_index = i
                        break
                
                if new_highlight_index != -1:
                    return valid_lines, new_highlight_index
        
        # If we get here, something went wrong with the text generation
        print(f"Warning: Generated text did not meet quality standards with {provider}")
        return None, -1
        
    except Exception as e:
        print(f"Error generating text with {provider}: {e}")
        return None, -1

# Import needed for random number generation inside this module
import random
