from flask import Flask, render_template, request, url_for, flash, redirect, make_response, app, abort
from data import db_session
from data import __all_models
from flask_uploads import UploadSet, configure_uploads, IMAGES
from header import header_logic, search_logic


def main(method, photos):
    db_sess = db_session.create_session()
    user_id = request.cookies.get('id')
    user = db_sess.query(__all_models.User).filter(__all_models.User.id == user_id).first()
    if method == 'GET':
        reviews_ = db_sess.query(__all_models.Reviews).filter(__all_models.Reviews.id_user == user_id)
        if user.img is not None:
            return render_template('profile.html', image_route=url_for('static', filename=f'pictures/{user.img}'),
                                   reviews=reviews_,  name=user.name, count_reviews=user.reviews_count,
                                   reg_data=user.created_date)
        else:
            return render_template('profile.html', image_route=url_for('static', filename='pictures/0.jpg'),
                                   name=user.name, count_reviews=user.reviews_count, reg_data=user.created_date,
                                   reviews=reviews_)
    else:
        if 'header_btn' in request.form:
            return header_logic()
        elif 'submit_btn' in request.form:
            return search_logic()
        else:
            if request.form['btn'] == 'write_new_review':
                return redirect('/writeReview')
            elif request.form['btn'] == 'edit_photo':
                img = request.files['file']
                filename = photos.save(img)
                user.img = filename
                db_sess.commit()
                return redirect('/profile')
            else:
                return 'ok'


def reviews_check(method):
    db_sess = db_session.create_session()
    user_id = request.cookies.get('id')
    if method == 'GET':
        reviews_ = db_sess.query(__all_models.Reviews).filter(__all_models.Reviews.id_user == user_id)
        return render_template('Reviews_form.html', reviews=reviews_, )
    else:
        if 'header_btn' in request.form:
            return header_logic()
        elif 'submit_btn' in request.form:
            return search_logic()
        else:
            if request.form['btn'] == 'change':
                return redirect('/change_review/<ind:id>')
            else:
                return redirect('/delete_review/<int:id>')


def delete_review(method, id):
    db_sess = db_session.create_session()
    user_id = request.cookies.get('id')
    review = db_sess.query(__all_models.Reviews).filter(__all_models.Reviews.id == id,
                                                        __all_models.Reviews.id_user == user_id).first()
    user = db_sess.query(__all_models.User).filter(__all_models.User.id == user_id).first()

    if review:
        films = db_sess.query(__all_models.Films).filter(__all_models.Films.title == review.title).first()
        marks = [int(i) for i in films.mark.split('_') if i != '']
        for i in marks:
            if i == int(review.mark):
                del marks[marks.index(i)]
                break
        films.mark = '_'.join([str(i) for i in marks if i != ''])
        films.countReviews -= 1
        if films.countReviews == 0:
            db_sess.delete(films)
        else:
            films.average_mark = sum([int(i) for i in films.mark.split('_')]) / films.countReviews
        db_sess.delete(review)
        user.reviews_count -= 1
        db_sess.commit()
    else:
        abort(404)
    return redirect('/news')


def change_review(method, id):
    db_sess = db_session.create_session()
    user_id = request.cookies.get('id')
    review_ = db_sess.query(__all_models.Reviews).filter(__all_models.Reviews.id == id,
                                                         __all_models.Reviews.id_user == user_id).first()
    if method == 'GET':
        return render_template('NewReviewForm.html', film_title=review_.title, mark_value=review_.mark,
                               year_film=review_.year, review_user=review_.review, btn_text='Изменить отзыв')
    else:
        if 'header_btn' in request.form:
            return header_logic()
        elif 'submit_btn' in request.form:
            return search_logic()
        else:
            title = request.form['movie_title']
            mark = request.form['mark']
            genre = request.form['genreOfFilm']
            year = request.form['movie_year']
            review = request.form['feedback']

            films = db_sess.query(__all_models.Films).filter(__all_models.Films.title == title).first()
            marks = [int(i) for i in films.mark.split('_')]
            for i in marks:
                if i == int(review_.mark):
                    marks[marks.index(i)] = mark
                    break
            films.mark = '_'.join([str(i) for i in marks])
            average_mark = sum([int(i) for i in marks]) / films.countReviews
            films.average_mark = average_mark

            review_.title = title
            review_.mark = mark
            review_.genre = genre
            review_.year = year
            review_.review = review
            db_sess.commit()
            return redirect('/news')
