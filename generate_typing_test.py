import os

# Define the answer key map from views.py to ensure correctness
# 11: 'a', 12: 'b', 13: 'c', 14: 'a', 15: 'b', 16: 'c', 17: 'a', 18: 'b', 19: 'c', 20: 'a'
# 21: 'b', 22: 'c', 23: 'a', 24: 'b', 25: 'c', 26: 'a', 27: 'b', 28: 'c', 29: 'a', 30: 'b'
# 31: 'c', 32: 'a', 33: 'b', 34: 'c', 35: 'a', 36: 'b', 37: 'c', 38: 'a', 39: 'b', 40: 'c'
# 41: 'a', 42: 'b', 43: 'c', 44: 'a', 45: 'b', 46: 'c', 47: 'a', 48: 'b', 49: 'c', 50: 'a'

# We will reuse the first 10 questions from the existing file if possible, or just redefine them to be safe/consistent.
# Let's redefine all 50 to ensuring perfect key alignment.

questions = [
    # 1-10: Basic Knowledge (Keys: b, c, b, a, c, b, a, c, b, a)
    # Note: I need to match the backend keys exactly.
    # Logic: 1->b (40-60 wpm), 2->c (ASDF...), 3->b (Touch typing), 4->a (Accuracy), 5->c (Index), 
    # 6->b (10 fingers), 7->a (Upright), 8->c (Practice), 9->b (WPM), 10->a (Focus accuracy)
    
    # 1 (b)
    ("What is considered a good average typing speed for office work?", [
        ("a", "10-20 WPM"), ("b", "40-60 WPM"), ("c", "90-100 WPM")
    ]),
    # 2 (c)
    ("Which keys are the 'Home Row' keys?", [
        ("a", "QWERTY UIOP"), ("b", "ZXCVB NM<>?"), ("c", "ASDFG HJKL")
    ]),
    # 3 (b)
    ("What is the technique of typing without looking at keys called?", [
        ("a", "Blind typing"), ("b", "Touch typing"), ("c", "Shadow typing")
    ]),
    # 4 (a)
    ("In professional typing, what is most important?", [
        ("a", "Accuracy"), ("b", "Loudness"), ("c", "Speed only")
    ]),
    # 5 (c)
    ("Which fingers rest on the 'F' and 'J' keys?", [
        ("a", "Thumbs"), ("b", "Pinky fingers"), ("c", "Index fingers")
    ]),
    # 6 (b)
    ("How many fingers should you utilize for maximum efficiency?", [
        ("a", "Two (Hunt and Peck)"), ("b", "All ten"), ("c", "Four")
    ]),
    # 7 (a)
    ("What is the correct posture for typing?", [
        ("a", "Back straight, feet flat"), ("b", "Slouching forward"), ("c", "Lying down")
    ]),
    # 8 (c)
    ("What is the best way to increase typing speed?", [
        ("a", "Typing harder"), ("b", "Looking at keys"), ("c", "Consistent practice")
    ]),
    # 9 (b)
    ("What does 'WPM' stand for?", [
        ("a", "Words Per Millisecond"), ("b", "Words Per Minute"), ("c", "Words Per Month")
    ]),
    # 10 (a)
    ("If you make many errors, what should you do?", [
        ("a", "Slow down and focus on accuracy"), ("b", "Type faster to compensate"), ("c", "Switch keyboards")
    ]),

    # 11-20: Keyboard Layout (Keys: a, b, c, a, b, c, a, b, c, a)
    # 11 (a)
    ("Where is the 'Esc' key usually located?", [
        ("a", "Top-left corner"), ("b", "Top-right corner"), ("c", "Bottom-left corner")
    ]),
    # 12 (b)
    ("Which key creates an uppercase letter?", [
        ("a", "Ctrl"), ("b", "Shift"), ("c", "Alt")
    ]),
    # 13 (c)
    ("To indent a paragraph, which key is commonly used?", [
        ("a", "Spacebar"), ("b", "Enter"), ("c", "Tab")
    ]),
    # 14 (a)
    ("The longest key on the keyboard is the:", [
        ("a", "Spacebar"), ("b", "Enter"), ("c", "Shift")
    ]),
    # 15 (b)
    ("Which key moves the cursor to the next line?", [
        ("a", "Backspace"), ("b", "Enter"), ("c", "Caps Lock")
    ]),
    # 16 (c)
    ("What key deletes the character to the LEFT of the cursor?", [
        ("a", "Delete"), ("b", "Space"), ("c", "Backspace")
    ]),
    # 17 (a)
    ("Which key deletes the character to the RIGHT of the cursor?", [
        ("a", "Delete"), ("b", "Backspace"), ("c", "Insert")
    ]),
    # 18 (b)
    ("The 'QWERTY' layout is named after:", [
        ("a", "Its inventor Mr. Qwerty"), ("b", "The first 6 letters on top row"), ("c", "A manufacturing code")
    ]),
    # 19 (c)
    ("The number pad is usually located on the:", [
        ("a", "Left side"), ("b", "Top center"), ("c", "Right side")
    ]),
    # 20 (a)
    ("Which key activates 'Overwrite' mode in many editors?", [
        ("a", "Insert"), ("b", "Home"), ("c", "End")
    ]),

    # 21-30: Typing Techniques (Keys: b, c, a, b, c, a, b, c, a, b)
    # 21 (b)
    ("Your wrists should be:", [
        ("a", "Resting firmly on the desk"), ("b", "Hovering or lightly resting on a pad"), ("c", "Bent upwards")
    ]),
    # 22 (c)
    ("The monitor should be positioned:", [
        ("a", "Above eye level"), ("b", "To your side"), ("c", "At eye level")
    ]),
    # 23 (a)
    ("Which finger types the 'A' key?", [
        ("a", "Left Pinky"), ("b", "Left Ring Finger"), ("c", "Left Index")
    ]),
    # 24 (b)
    ("Which finger types the 'L' key?", [
        ("a", "Right Index"), ("b", "Right Ring Finger"), ("c", "Right Pinky")
    ]),
    # 25 (c)
    ("Which thumb should press the Spacebar?", [
        ("a", "Only the left"), ("b", "Only the right"), ("c", "Whichever is more comfortable (or alternate)")
    ]),
    # 26 (a)
    ("The 'Bump' on F and J helps you:", [
        ("a", "Find home row without looking"), ("b", "Clean your fingers"), ("c", "Press harder")
    ]),
    # 27 (b)
    ("When typing numbers on the top row, you should:", [
        ("a", "Use the numpad only"), ("b", "Reach up from home row"), ("c", "Look at your hands")
    ]),
    # 28 (c)
    ("Constant looking at the keyboard causes:", [
        ("a", "Higher speed"), ("b", "Better accuracy"), ("c", "Slower speed and neck strain")
    ]),
    # 29 (a)
    ("Ergonomics helps prevent:", [
        ("a", "Repetitive Strain Injury (RSI)"), ("b", "Computer viruses"), ("c", "Spelling errors")
    ]),
    # 30 (b)
    ("How often should you take breaks?", [
        ("a", "Never"), ("b", "Every 20-30 minutes"), ("c", "Only when in pain")
    ]),

    # 31-40: Speed & Accuracy (Keys: c, a, b, c, a, b, c, a, b, c)
    # 31 (c)
    ("To type faster, you should first:", [
        ("a", "Buy a mechanical keyboard"), ("b", "Type forcefully"), ("c", "Master accuracy")
    ]),
    # 32 (a)
    ("A 'typo' is:", [
        ("a", "A typographical error"), ("b", "A type of font"), ("c", "A fast typist")
    ]),
    # 33 (b)
    ("Standard typing tests measure speed in?", [
        ("a", "KPH (Keys Per Hour)"), ("b", "WPM (Words Per Minute)"), ("c", "LPS (Lines Per Second)")
    ]),
    # 34 (c)
    ("One 'Word' in WPM calculation is typically:", [
        ("a", "3 characters"), ("b", "10 characters"), ("c", "5 characters (including space)")
    ]),
    # 35 (a)
    ("Gross WPM minus errors determines:", [
        ("a", "Net WPM"), ("b", "Raw Speed"), ("c", "Total Keystrokes")
    ]),
    # 36 (b)
    ("If you type 300 characters in 1 minute, your WPM is approx:", [
        ("a", "30"), ("b", "60"), ("c", "100")
    ]),
    # 37 (c)
    ("Rushing usually leads to:", [
        ("a", "Promotion"), ("b", "Higher Net WPM"), ("c", "More mistakes and lower Net WPM")
    ]),
    # 38 (a)
    ("Using proper finger placement reduces:", [
        ("a", "Hand fatigue"), ("b", "Computer speed"), ("c", "Screen brightness")
    ]),
    # 39 (b)
    ("The 'Ctrl + C' shortcut is for:", [
        ("a", "Cut"), ("b", "Copy"), ("c", "Close")
    ]),
    # 40 (c)
    ("The 'Ctrl + V' shortcut is for:", [
        ("a", "Verify"), ("b", "View"), ("c", "Paste")
    ]),

    # 41-50: Professional Typing (Keys: a, b, c, a, b, c, a, b, c, a)
    # 41 (a)
    ("In a formal document, how many spaces after a period?", [
        ("a", "One"), ("b", "Two"), ("c", "Three")
    ]),
    # 42 (b)
    ("What should you do before submitting typed work?", [
        ("a", "Save it only"), ("b", "Proofread it"), ("c", "Close the laptop")
    ]),
    # 43 (c)
    ("Which font is commonly used for professional documents?", [
        ("a", "Comic Sans"), ("b", "Papyrus"), ("c", "Times New Roman or Arial")
    ]),
    # 44 (a)
    ("Blind Carbon Copy (BCC) is used in:", [
        ("a", "Emailing"), ("b", "Printing"), ("c", "Saving files")
    ]),
    # 45 (b)
    ("Touch typing allows you to focus on:", [
        ("a", "The keyboard"), ("b", "The content on screen"), ("c", "Your fingers")
    ]),
    # 46 (c)
    ("Data Entry jobs require high:", [
        ("a", "Creativity"), ("b", "Volume"), ("c", "Accuracy and Speed")
    ]),
    # 47 (a)
    ("Shortcuts like Ctrl+Z (Undo) help to:", [
        ("a", "Correct mistakes quickly"), ("b", "Delete files"), ("c", "Zoom in")
    ]),
    # 48 (b)
    ("Maintaining a consistent rhythm helps with:", [
        ("a", "Typing louder"), ("b", "Fluidity and speed"), ("c", "Breaking keys")
    ]),
    # 49 (c)
    ("Capitalizing every word is:", [
        ("a", "Professional"), ("b", "Easy to read"), ("c", "Incorrect grammar (Title Case excluded)")
    ]),
    # 50 (a)
    ("A professional typist aims for accuracy of:", [
        ("a", "95-100%"), ("b", "50-60%"), ("c", "75%")
    ])
]

# Generate HTML
html_content = r"""{% extends 'base_complete.html' %}

{% block title %}Typing Test - ErrandExpress{% endblock %}

{% block content %}
<div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-gradient-to-r from-primary to-indigo-600 text-white">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div class="text-center">
                <h1 class="text-3xl font-bold mb-2">⌨️ Typing Skills Test</h1>
                <p class="text-blue-100">Answer all questions to validate your typing skills</p>
                <div class="mt-4 inline-flex items-center gap-2 bg-white/10 px-4 py-2 rounded-lg">
                    <i data-lucide="info" class="w-5 h-5"></i>
                    <span class="font-semibold">Passing Score: 75% (38/50 correct)</span>
                </div>
            </div>
        </div>
    </div>

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        <!-- Instructions -->
        <div class="bg-blue-50 border-2 border-blue-200 rounded-2xl p-6 mb-8">
            <div class="flex items-start gap-3">
                <i data-lucide="alert-circle" class="w-6 h-6 text-blue-600 mt-1"></i>
                <div>
                    <h3 class="font-bold text-gray-900 mb-2">Test Instructions</h3>
                    <ul class="text-sm text-gray-700 space-y-1 list-disc list-inside">
                        <li>This test contains <strong>50 multiple choice questions</strong>.</li>
                        <li>You need to score 75% or higher (38+ correct) to pass.</li>
                        <li>Select one answer for each question.</li>
                        <li>Click "Submit Test" at the bottom when finished.</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- Test Form -->
        <form method="post" id="typing-test-form">
            {% csrf_token %}
            
            <div class="space-y-6">
"""

for i, (q_text, opts) in enumerate(questions, 1):
    html_content += f"""
                <!-- Question {i} -->
                <div class="bg-white rounded-2xl p-6 shadow-sm border-2 border-gray-100">
                    <h3 class="font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <span class="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center text-sm">{i}</span>
                        {q_text}
                    </h3>
                    <div class="space-y-3 ml-10">
"""
    for val, label in opts:
        html_content += f"""                        <label class="flex items-center gap-3 p-3 rounded-lg border-2 border-gray-200 hover:border-primary hover:bg-blue-50 cursor-pointer transition-all">
                            <input type="radio" name="question_{i}" value="{val}" required class="w-5 h-5 text-primary">
                            <span>{label}</span>
                        </label>
"""
    html_content += """                    </div>
                </div>
"""

html_content += r"""            </div>

            <!-- Submit Button -->
            <div class="mt-8 flex justify-center">
                <button type="submit" class="px-8 py-4 bg-gradient-to-r from-primary to-blue-600 text-white font-bold rounded-lg hover:shadow-lg transition-all text-lg flex items-center gap-3">
                    <i data-lucide="check-circle" class="w-6 h-6"></i>
                    Submit Test
                </button>
            </div>
        </form>

    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
// Initialize Lucide icons
lucide.createIcons();

// Form validation
document.getElementById('typing-test-form').addEventListener('submit', function(e) {
    const questions = 50;
    let answered = 0;
    
    // Check all 50 questions
    for (let i = 1; i <= questions; i++) {
        const radios = document.getElementsByName(`question_${i}`);
        const isAnswered = Array.from(radios).some(radio => radio.checked);
        if (isAnswered) answered++;
    }
    
    if (answered < questions) {
        e.preventDefault();
        alert(`Please answer all questions. You've answered ${answered} out of ${questions}.`);
        
        // Scroll to first unanswered question
        for (let i = 1; i <= questions; i++) {
            const radios = document.getElementsByName(`question_${i}`);
            const isAnswered = Array.from(radios).some(radio => radio.checked);
            if (!isAnswered) {
                radios[0].closest('.bg-white').scrollIntoView({behavior: 'smooth', block: 'center'});
                break;
            }
        }
        return false;
    }
    
    // Confirm submission
    if (!confirm('Are you sure you want to submit your test? You can only take this test once.')) {
        e.preventDefault();
        return false;
    }
});

// Highlight selected answers
document.querySelectorAll('input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', function() {
        // Remove highlight from all labels in this question
        const questionDiv = this.closest('.bg-white');
        questionDiv.querySelectorAll('label').forEach(label => {
            label.classList.remove('border-primary', 'bg-blue-50');
            label.classList.add('border-gray-200');
        });
        
        // Highlight selected label
        const selectedLabel = this.closest('label');
        selectedLabel.classList.remove('border-gray-200');
        selectedLabel.classList.add('border-primary', 'bg-blue-50');
    });
});
</script>
{% endblock %}
"""

output_path = r"c:\Users\Admin\Desktop\errandexpress - Copy\errandexpress\core\templates\skills\typing_test.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Successfully generated {output_path} with {len(questions)} questions.")
