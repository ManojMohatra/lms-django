from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Course,Enrollment


courses = list(Course.objects.all())

documents = [
    (c.title + " " + c.description).lower()
    for c in courses
    ]

vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(documents)

similarity_matrix = cosine_similarity(tfidf_matrix)

def recommend_for_user(user,top_n=3):
    enrolled_courses = Enrollment.objects.filter(student=user)
    enrolled_ids = [e.course.id for e in enrolled_courses]

    if not enrolled_ids:
        return Course.objects.order_by('-id')[:5]

    recommended_scores = {}

    for enrolled_id in enrolled_ids:
        index = next(
            (i for i,c in enumerate(courses) if c.id == enrolled_id),
            None
            )

        if index is None:
            continue

        for i, score in enumerate(similarity_matrix[index]):
            course_id = courses[i].id

            if course_id not in enrolled_ids:
                recommended_scores[course_id] = max(
                    recommended_scores.get(course_id,0),
                    score
                    )
    sorted_courses = sorted(
        recommended_scores.items(),
        key=lambda x: x[1],
        reverse=True
        )

    top_ids = [cid for cid, _ in sorted_courses[:top_n]]

    return Course.objects.filter(id__in=top_ids)

