import nltk
from nltk.tokenize import sent_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from heapq import nlargest

from .models import Intern, InternReport  # Adjust import as needed
# If running as a script, set up Django environment first

nltk.download('stopwords')
nltk.download('punkt')

def summarize_section_new_learning(section_name):
    # Gather all new learning texts for interns in the given section
    interns = Intern.objects.filter(section=section_name)
    reports = InternReport.objects.filter(intern__in=interns)
    all_text = " ".join([report.new_learning for report in reports if hasattr(report, 'new_learning') and report.new_learning])

    if not all_text.strip():
        print("No new learning data found for this section.")
        return

    sentences = sent_tokenize(all_text)
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    words = []
    for sentence in sentences:
        for word in nltk.word_tokenize(sentence):
            if word.lower() not in stop_words and word.isalpha():
                words.append(stemmer.stem(word))

    freq_dist = nltk.FreqDist(words)
    top_words = [word[0] for word in freq_dist.most_common(10)]

    summary = []
    for sentence in sentences:
        sentence_words = nltk.word_tokenize(sentence.lower())
        sentence_score = 0
        for word in sentence_words:
            if stemmer.stem(word) in top_words:
                sentence_score += 1
        summary.append((sentence, sentence_score))

    for sentence in nlargest(3, summary, key=lambda x: x[1]):
        print(sentence[0])

# Example usage:
# summarize_section_new_learning('Section A')