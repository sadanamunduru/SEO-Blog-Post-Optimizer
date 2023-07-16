import requests
from bs4 import BeautifulSoup
import nltk
import time
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from googlesearch import search
import streamlit as st
import spacy
from collections import Counter
import textstat
import urllib3
from urllib.error import HTTPError
from requests.exceptions import HTTPError
import matplotlib.pyplot as plt
import pandas as pd
import altair as alt
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words = set(stopwords.words("english"))

nlp = spacy.load("en_core_web_sm")


# Keyword Analysis
def suggest_keywords(content):
    doc = nlp(content)
    keywords = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop]
    freq_dist = Counter(keywords)
    return freq_dist.most_common(5)


# On-Page Optimization
def optimize_on_page_elements(content):
    recommendations = []
    doc = nlp(content)

    # Recommendation for meta tags
    if len(doc.text) > 160:
        recommendations.append('Your meta description is too long.')
    elif len(doc.text) < 70:
        recommendations.append('Your meta description is too short.')

    # Recommendation for headings
    num_headings = content.count('<h1>') + content.count('<h2>') + content.count('<h3>') + content.count(
        '<h4>') + content.count('<h5>') + content.count('<h6>')
    if num_headings == 0:
        recommendations.append('You have no headings. Consider adding some for better SEO.')


    recommendations.append('Check your URL structure to ensure it is SEO friendly.')
    recommendations.append('Ensure your images have appropriate alt tags.')
    recommendations.append('Check your internal linking structure to ensure a good user experience.')

    return recommendations


# Content Analysis
def analyze_content(content, target_keywords):
    word_count = len(content.split())
    readability_score = textstat.flesch_reading_ease(content)
    keyword_density = calculate_keyword_density(content, target_keywords)
    return word_count, readability_score, keyword_density


# Calculate Keyword Density
def calculate_keyword_density(content, target_keywords):
    tokens = nltk.word_tokenize(content)
    stop_words = set(nltk.corpus.stopwords.words("english"))
    filtered_tokens = [token.lower() for token in tokens if token.lower() not in stop_words and token.isalpha()]
    keyword_count = sum(filtered_tokens.count(keyword.lower()) for keyword in target_keywords)
    total_words = len(filtered_tokens)

    if total_words > 0:
        return keyword_count / total_words
    else:
        return 0.0


# SEO Score Calculation
def calculate_seo_score(content, target_keywords):
    keyword_density = calculate_keyword_density(content, target_keywords)
    readability_score = textstat.flesch_reading_ease(content)
    seo_score = (keyword_density + (206 - readability_score) / 10) / 2
    return seo_score


def fetch_webpage_content(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.text
    except Exception as e:
        print(f"Error while fetching webpage content: {e}")
        return None


def extract_keywords(webpage_content):
    tokens = word_tokenize(webpage_content)
    filtered_tokens = [word.lower() for word in tokens if word.lower() not in stop_words and word.isalpha()]
    freq_dist = FreqDist(filtered_tokens)
    most_common_keywords = freq_dist.most_common(5)
    return most_common_keywords


# # Competitor content dictionary in case http request are failing
# competitor_contents = {
#     'Competitor1': 'Predefined content for Competitor1',
#     'Competitor2': 'Predefined content for Competitor2',
#     'Competitor3': 'Predefined content for Competitor3',
# }


def analyze_competitors(niche, target_keywords):
    competitors = {
        'Competitor1': '',
        'Competitor2': '',
        'Competitor3': ''
    }
    insights = []
    all_keywords = []  # collect all keywords here

    for competitor in competitors.keys():
        competitor_insight = f"<span style='font-weight: bold; color: #00008B; font-size: 20px;'>Competitor: {competitor}</span>\n"

        # Perform a search query for the competitor and niche
        query = f"{competitor} {niche}"
        search_results = list(search(query, num_results=1))
        if not search_results:
            competitor_insight += "No search results found for the competitor.\n"
            insights.append(competitor_insight)
            continue

        search_result = search_results[0]
        competitor_url = search_result

        # Fetch the webpage content for the search result
        webpage_content = fetch_webpage_content(competitor_url)

        if webpage_content is None:
            competitor_insight += "Unable to fetch the content. Check the URL or the website's accessibility."
            insights.append(competitor_insight)
            continue

        # Extract the top 5 keywords from the webpage content
        blog_keywords = extract_keywords(webpage_content)[:5]

        all_keywords.extend(blog_keywords)  # add the keywords to our list

        competitor_insight += f"<span style='font-weight: bold;'>Keywords:</span>\n"
        for keyword, count in blog_keywords:
            competitor_insight += f"- {keyword} ({count} occurrences)\n"

        competitor_insight += f"<span style='font-weight: bold;'>Link:</span> {competitor_url}\n\n"
        insights.append(competitor_insight)

    # Get the 5 most common keywords from all_keywords
    most_common_keywords = Counter(all_keywords).most_common(5)

    return insights, most_common_keywords


def generate_serp_preview(title, description, content):
    MAX_LINES = 4  # Maximum number of lines to display

    # Truncate content if it exceeds the maximum number of lines
    lines = content.split('\n')
    if len(lines) > MAX_LINES:
        lines = lines[:MAX_LINES]
        content = '\n'.join(lines) + '...'

    serp_preview = f"<div style='background-color: #f8f9fa; padding: 10px;'>"
    serp_preview += f"<h3 style='margin: 0;'><a href='#'>{title}</a></h3>"
    serp_preview += f"<cite style='color: #006621; font-size: 14px;'>www.example.com</cite>"
    serp_preview += f"<p style='margin: 0; color: #545454;'>{description}</p>"
    serp_preview += f"<p>{content}</p>"
    serp_preview += f"</div>"
    return serp_preview

# Function to generate bar chart
def generate_bar_chart(labels, values, title, x_label, y_label):
    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    st.pyplot(fig)
    

# Function to generate speedometer chart

def generate_speedometer_chart(value, min_value, max_value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={'axis': {'range': [min_value, max_value]},
               'bar': {'color': "darkblue"},
               'bgcolor': "white",
               'borderwidth': 2,
               'bordercolor': "gray",
               'steps': [
                   {'range': [min_value, max_value], 'color': 'lightgray'}],
               'threshold': {'line': {'color': "red", 'width': 4},
                             'thickness': 0.75,
                             'value': value}}))

    return fig
    
def main():
    st.title("SEO Blog Post Optimizer")
    option = st.radio("Select an option", ("Enter blog post content", "Paste web page link"), key="option_selection")

    word_count = 0
    readability_score = 0
    keyword_density = 0.0
    seo_score = 0.0
    content = ""

    if option == "Enter blog post content":
        content = st.text_area("Enter your blog post content")
        niche = st.text_input("Enter your niche")
        title = st.text_input("Enter the title of your blog post")
        description = st.text_input("Enter the meta description of your blog post")
        target_keywords = st.text_input("Enter the target keywords (separated by commas)").split(",")
        target_keywords = [keyword.strip().lower() for keyword in target_keywords]
    elif option == "Paste web page link":
        target_keywords = st.text_input("Enter the target keywords (separated by commas)").split(",")
        target_keywords = [keyword.strip().lower() for keyword in target_keywords]
        web_link = st.text_input("Paste the web page link")
        if st.button("Scrape Content"):
            content = fetch_webpage_content(web_link)
            if content is None:
                st.error("Failed to scrape the content from the provided link. Please check the link and try again.")
                return
        else:
            return
    else:
        return

    suggested_keywords = suggest_keywords(content)
    recommendations = optimize_on_page_elements(content)

    if content:
        word_count, readability_score, keyword_density = analyze_content(content, target_keywords)
        seo_score = calculate_seo_score(content, target_keywords)

    if option == "Enter blog post content":
        competitor_insights, most_common_keywords = analyze_competitors(niche, target_keywords)

    if option == "Enter blog post content":
        serp_preview = generate_serp_preview(title, description, content)

    st.sidebar.markdown("<h2 style='color: #00008B; font-size: 20px;'>Blog Analysis</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.subheader("Keyword Analysis")
    keyword_labels = [keyword for keyword, _ in suggested_keywords]
    keyword_counts = [count for _, count in suggested_keywords]
    keyword_df = pd.DataFrame({"Keywords": keyword_labels, "Counts": keyword_counts})
    st.sidebar.bar_chart(keyword_df.set_index("Keywords"))
    st.sidebar.write(keyword_df)

    # Content Analysis
    st.sidebar.markdown("---")
    st.sidebar.subheader("Content Analysis")
    st.sidebar.markdown("#### Word Count")
    if word_count >= 300:
        st.sidebar.markdown(f"Value: {word_count} (<span style='color: green; font-weight: bold;'>Optimal</span>)", unsafe_allow_html=True)
    elif word_count >= 200:
        st.sidebar.markdown(f"Value: {word_count} (<span style='color: orange; font-weight: bold;'>Good</span>)", unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"Value: {word_count} (<span style='color: red; font-weight: bold;'>Low</span>)", unsafe_allow_html=True)

    st.sidebar.markdown("#### Readability Score")
    if readability_score >= 70:
        st.sidebar.markdown(f"Value: {readability_score} (<span style='color: green; font-weight: bold;'>Optimal</span>)", unsafe_allow_html=True)
    elif readability_score >= 50:
        st.sidebar.markdown(f"Value: {readability_score} (<span style='color: orange; font-weight: bold;'>Good</span>)", unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"Value: {readability_score} (<span style='color: red; font-weight: bold;'>Low</span>)", unsafe_allow_html=True)

    st.sidebar.markdown("#### Keyword Density")
    if 0.03 <= keyword_density <= 0.04:
        st.sidebar.markdown(f"Value: {keyword_density} (<span style='color: green; font-weight: bold;'>Optimal</span>)", unsafe_allow_html=True)
    elif 0.02 <= keyword_density < 0.03:
        st.sidebar.markdown(f"Value: {keyword_density} (<span style='color: orange; font-weight: bold;'>Good</span>)", unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"Value: {keyword_density} (<span style='color: red; font-weight: bold;'>Low</span>)", unsafe_allow_html=True)

    st.subheader("SEO Score")
    st.plotly_chart(generate_speedometer_chart(seo_score, 0, 10, "SEO Score"))

    st.markdown("---")

    # On-Page Optimization
    st.subheader("On-Page Optimization")
    for rec in recommendations:
        st.write(rec)

    if option == "Enter blog post content":
        # Recommended Keywords
        st.markdown("### Recommended Keywords")
        st.markdown("Try to add the below keywords to your content to increase the search engine appearance score against given niche. The values beside indicates the frequencies in your competitors blogs")
        for keyword in most_common_keywords[:5]:
            st.markdown(f"- {keyword[0]}")

        st.subheader("Competitor Analysis")
        for insight in competitor_insights:
            st.markdown(insight, unsafe_allow_html=True)

        st.subheader("SERP Preview")
        st.markdown(serp_preview, unsafe_allow_html=True)

    st.write("---")
    st.write("Thank you for using SEO Blog Post Optimizer!")


if __name__ == '__main__':
    main()
