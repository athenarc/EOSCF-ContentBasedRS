from app.recommenders.autocompletion.enumerated_field_suggestions.suggestion_generation import \
    get_suggestions_for_enumerated_fields
from app.recommenders.autocompletion.tag_suggestions.suggestion_generation import \
    get_suggestions_for_tags
from app.settings import APP_SETTINGS


def _get_enumerated_fields(fields_list):
    enum_fields = APP_SETTINGS["BACKEND"]["AUTO_COMPLETION"]["ENUMERATED_FIELDS"].keys()
    return list(set(fields_list).intersection(set(enum_fields)))


def inject_extracted_enumerated_fields(suggestions, extracted_enumerated_fields):
    priorities = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    for field, values in extracted_enumerated_fields.items():
        if field in suggestions:
            field_and_prio = []
            for value in values:
                if value in suggestions[field]:
                    # Both extracted and suggested from similar services
                    field_and_prio.append((value, priorities['HIGH']))
                else:
                    # Only extracted
                    field_and_prio.append((value, priorities['MEDIUM']))

            for value in suggestions[field]:
                if value not in values:
                    # Only suggested from similar services
                    field_and_prio.append((value, priorities['LOW']))

            suggestions[field] = [value for value, prio in sorted(field_and_prio, key=lambda x: x[1], reverse=True)]


def get_auto_completion_suggestions(new_service, fields_to_suggest, maximum_suggestions, existing_fields_values):
    # Get suggestions for enumerated fields
    requested_enumerated_fields = _get_enumerated_fields(fields_to_suggest)

    suggestions = get_suggestions_for_enumerated_fields(new_service=new_service,
                                                        requested_fields=requested_enumerated_fields,
                                                        maximum_suggestions=maximum_suggestions,
                                                        existing_fields_values=existing_fields_values)

    if "tags" in fields_to_suggest:
        # Get suggestions for tags
        suggestions_for_tags, extracted_enumerated_fields \
            = get_suggestions_for_tags(service_attributes=new_service,
                                       existing_values=existing_fields_values["tags"]
                                       if "tags" in existing_fields_values else [],
                                       max_num=maximum_suggestions)

        suggestions["tags"] = suggestions_for_tags

        inject_extracted_enumerated_fields(suggestions, extracted_enumerated_fields)

    return suggestions
