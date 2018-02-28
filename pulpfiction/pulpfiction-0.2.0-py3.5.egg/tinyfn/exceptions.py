from .validator import Comment as CommentValidator


class LanguageUnsupported(BaseException):

    @classmethod
    def from_validator(cls, validator: CommentValidator):
        msg = (
            'Comment "{text}" detected to be not in \'{language_code}\':'
            'at: {path}:{line_num}'.format(
                text=validator.comment.text,
                language_code=validator.language_code,
                path=validator.comment.filepath,
                line_num=validator.comment.line_num
            )
        )
        return cls(msg)
