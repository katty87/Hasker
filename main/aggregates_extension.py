from django.db.models import Aggregate, CharField


class GroupConcat(Aggregate):
    function = 'STRING_AGG'
    allow_distinct = True

    def __init__(self, expression, distinct=False, ordering=None, **extra):
        super(GroupConcat, self).__init__(
            expression,
            distinct='DISTINCT ' if distinct else '',
            ordering=' ORDER BY %s' % ordering if ordering is not None else '',
            output_field=CharField(),
            **extra
        )

    def as_sql(self, compiler, connection, **extra_context):
        sql, params = super().as_sql(
            compiler, connection,  **extra_context
        )
        sql_len = len(sql)
        return sql[:sql_len-1] + ',\',\')', params
