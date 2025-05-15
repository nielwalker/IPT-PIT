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
    all_text = " ".join([report.new_learnings for report in reports if hasattr(report, 'new_learning') and report.new_learnings])

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

def summarize_intern_new_learning(intern_id):
    reports = InternReport.objects.filter(intern_id=intern_id)
    all_text = " ".join([report.new_learnings for report in reports if hasattr(report, 'new_learnings') and report.new_learnings])
    if not all_text.strip():
        return "No new learnings submitted."

    # NLTK-based extractive summarization
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    import nltk

    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

    sentences = sent_tokenize(all_text)
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    words = []
    for sentence in sentences:
        for word in word_tokenize(sentence):
            if word.lower() not in stop_words and word.isalpha():
                words.append(stemmer.stem(word))

    freq_dist = nltk.FreqDist(words)
    top_words = [word[0] for word in freq_dist.most_common(10)]

    scored_sentences = []
    for sentence in sentences:
        sentence_words = word_tokenize(sentence.lower())
        sentence_score = 0
        for word in sentence_words:
            if stemmer.stem(word) in top_words:
                sentence_score += 1
        scored_sentences.append((sentence, sentence_score))

    # Get top 3 sentences as summary
    from heapq import nlargest
    summary_sentences = [s[0] for s in nlargest(3, scored_sentences, key=lambda x: x[1])]
    return " ".join(summary_sentences)

# Example usage:
# summarize_section_new_learning('Section A')