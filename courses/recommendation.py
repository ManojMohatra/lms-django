from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Count
from .models import Course, Enrollment


def build_similarity():
    courses = list(Course.objects.all())

    if not courses:
        return courses, None

    documents = []

    for c in courses:
        tags_text = " ".join(tag.name for tag in c.tags.all())

        # Weighted text (title more important than description)
        doc = (
            (c.title + " ") * 3 +          # strong weight
            (c.description + " ") * 1 +    # normal weight
            (tags_text + " ") * 2          # tag importance
        ).lower()

        documents.append(doc)

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity_matrix = cosine_similarity(tfidf_matrix)

    return courses, similarity_matrix


# ─────────────────────────────────────────────────────────────
# Main Recommendation Function
# ─────────────────────────────────────────────────────────────
def recommend_for_user(user, top_n=5):
    courses, similarity_matrix = build_similarity()

    if not courses or similarity_matrix is None:
        return Course.objects.none()

    # Get enrolled courses
    enrolled_courses = Enrollment.objects.filter(student=user)
    enrolled_ids = [e.course.id for e in enrolled_courses]

    # ─────────────────────────────────────────
    # Cold start (new user)
    # ─────────────────────────────────────────
    if not enrolled_ids:
        return (
            Course.objects.annotate(num_students=Count("enrollments"))
            .order_by("-num_students", "-created_at")[:top_n]
        )

    recommended_scores = {}

    # ─────────────────────────────────────────
    # Compute similarity-based scores
    # ─────────────────────────────────────────
    for enrolled_id in enrolled_ids:
        index = next(
            (i for i, c in enumerate(courses) if c.id == enrolled_id),
            None
        )

        if index is None:
            continue

        enrolled_course = courses[index]

        for i, score in enumerate(similarity_matrix[index]):
            course = courses[i]

            if course.id in enrolled_ids:
                continue

            final_score = score

            # ─────────────────────────────
            # Boost: Same difficulty
            # ─────────────────────────────
            if course.difficulty == enrolled_course.difficulty:
                final_score += 0.15

            # ─────────────────────────────
            # Boost: Same tags overlap
            # ─────────────────────────────
            enrolled_tags = set(enrolled_course.tags.values_list("id", flat=True))
            course_tags = set(course.tags.values_list("id", flat=True))

            overlap = len(enrolled_tags & course_tags)
            if overlap > 0:
                final_score += overlap * 0.05

            # ─────────────────────────────
            # Boost: Popularity
            # ─────────────────────────────
            popularity = Enrollment.objects.filter(course=course).count()
            final_score += min(popularity * 0.01, 0.2)

            # ─────────────────────────────
            # Boost: Recency (newer courses)
            # ─────────────────────────────
            days_old = (course.created_at - enrolled_course.created_at).days
            if days_old > 0:
                final_score += min(days_old * 0.001, 0.1)

            # Keep best score
            recommended_scores[course.id] = max(
                recommended_scores.get(course.id, 0),
                final_score
            )

    # ─────────────────────────────────────────
    # Sort and return
    # ─────────────────────────────────────────
    sorted_courses = sorted(
        recommended_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top_ids = [cid for cid, _ in sorted_courses[:top_n]]

    # Preserve order
    preserved = {cid: index for index, cid in enumerate(top_ids)}
    return sorted(
        Course.objects.filter(id__in=top_ids),
        key=lambda x: preserved[x.id]
    )
