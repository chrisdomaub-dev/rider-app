from django.db.models import FloatField, Func


class Haversine(Func):
    """
    Harversine function used to calculate geographical distance between coordinates.

    Usage:
        - Harversine(F(field_lat1), F(field_lng2), F(field_lat2), F(field_lng2))
        - Harversine(Value(123), Value(123), F(field_lat2), F(field_lng2))
        - Or any 4 parameter combination of defined value and field value.
    """

    output_field = FloatField()

    def as_sql(self, compiler, connection, **extra_context):
        compiled = [compiler.compile(expr) for expr in self.source_expressions]

        if len(compiled) != 4:
            raise ValueError("Haversine requires 4 arguments (lat1, lng1, lat2, lng2)")

        lat1_sql, lat1_params = compiled[0]
        lng1_sql, lng1_params = compiled[1]
        lat2_sql, lat2_params = compiled[2]
        lng2_sql, lng2_params = compiled[3]

        sql_template = (
            "(6371 * acos("
            f"cos(radians({lat1_sql})) * cos(radians({lat2_sql})) * "
            f"cos(radians({lng2_sql}) - radians({lng1_sql})) + "
            f"sin(radians({lat1_sql})) * sin(radians({lat2_sql}))"
            f"))"
        )

        # Compile parameters to match their usage position in the sql template.
        params = []
        params += lat1_params
        params += lat2_params
        params += lng2_params
        params += lng1_params
        params += lat1_params
        params += lat2_params

        return sql_template, params
