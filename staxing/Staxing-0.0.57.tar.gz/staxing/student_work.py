"""Staxing test files - Helper."""

from helper import Student
from selenium.webdriver.common.by import By

for _id in range(1, 30):
    student = Student(
        username='student' + str(('0' if _id < 10 else '')) + str(_id),
        password='staxly16',
        site='tutor-demo.openstax.org')
    student.set_window_size(height=700, width=1200)
    student.change_wait_time(3)
    student.login()
    courses = student.get_course_list()
    for index in range(0, len(courses)):
        course = courses[index]
        student.select_course(title=course.get_attribute('data-title'))
        try:
            student.find(
                By.XPATH,
                '//button[contains(text(),"Start your free trial")]') \
                .click()
        except Exception:
            pass
        try:
            tooltip = student.find(
                By.CSS_SELECTOR, '.joyride-tooltip__button--primary')
            while(tooltip):
                student.sleep(0.5)
                tooltip.click()
                tooltip = student.find(
                    By.CSS_SELECTOR, '.joyride-tooltip__button--primary')
        except Exception:
            pass
        student.goto_course_list()
        courses = student.get_course_list()
    student.delete()
