import itertools

import pandas as pd
from app.databases.registry.registry_selector import get_registry
from app.recommenders.autocompletion.tag_suggestions.components.filtering.deduplication import \
    _overlapping_keywords
from app.recommenders.autocompletion.tag_suggestions.suggestion_generation import \
    get_suggestions_for_tags
from app.settings import APP_SETTINGS
from tqdm import tqdm

ANNOTATIONS = "app/recommenders/autocompletion/tag_suggestions/" \
              "evaluation/manual_annotation/storage/tags_annotation.xlsx"

JOINED_ANNOTATIONS = "app/recommenders/autocompletion/tag_suggestions/" \
                     "evaluation/manual_annotation/storage/joined_annotations.csv"


def merge_services():
    annotations = [annotation for _, annotation in pd.read_excel(ANNOTATIONS, sheet_name=None).items()]

    final_df = annotations[0]
    for df in annotations[1:]:
        final_df = final_df.merge(df, how="outer", on="Id")

    final_df['Name'] = final_df.apply(
        lambda row: row['Name_x'] if not pd.isnull(row['Name_x']) else row['Name_y'], axis=1
    )

    # Drop index columns that were created by excel
    final_df = final_df.drop(columns=[column for column in final_df.columns
                                      if "Unnamed" in column or "Name_" in column])

    return final_df


def split_tags(tags_per_annotator):
    return [set([tag for tag in tags.split(",")])
            for tags in tags_per_annotator if not pd.isnull(tags)]


def find_primary_tags(tag_sets):
    return tag_sets[0].intersection(tag_sets[1])


def find_secondary_tags(tag_sets):
    # (S1 U S2) - (S1 Π S2)
    return tag_sets[0].union(tag_sets[1]).difference(tag_sets[0].intersection(tag_sets[1]))


def find_all_tags(tag_sets):
    return tag_sets[0].union(tag_sets[1])


def join_tags(final_df):
    final_df['Primary'] = final_df.apply(
        lambda row: find_primary_tags(
            split_tags(
                row[[column for column in final_df.columns if "tags" in column]]
            )
        ), axis=1
    )

    final_df['Secondary'] = final_df.apply(
        lambda row: find_secondary_tags(
            split_tags(
                row[[column for column in final_df.columns if "tags" in column]]
            )
        ), axis=1
    )

    final_df['All'] = final_df.apply(
        lambda row: find_all_tags(
            split_tags(
                row[[column for column in final_df.columns if "tags" in column]]
            )
        ), axis=1
    )


def tag_preprocessing(tags):
    text_processor = APP_SETTINGS["BACKEND"]["TEXT_PROCESSOR"]

    ret_tags = {tag.lstrip().rstrip() for tag in tags}
    ret_tags = {tag.lower() for tag in ret_tags}
    ret_tags = {text_processor.lemmatization(tag) for tag in ret_tags}

    removed_tags = set()
    for tag_1, tag_2 in list(itertools.permutations(ret_tags, 2)):
        if _overlapping_keywords(tag_1, tag_2) and len(tag_1) > len(tag_2):
            removed_tags.add(tag_2)

    return ret_tags.difference(removed_tags)


def get_tags_of_services(df, max_num):
    db = get_registry()

    tqdm.pandas()
    df['Generated'] = df.progress_apply(  # Using the tqdm progress bar
        lambda row: get_suggestions_for_tags(db.get_service(row['Id']), max_num=max_num), axis=1
    )


def lemmatize_tag_set(tag_set):
    text_processor = APP_SETTINGS["BACKEND"]["TEXT_PROCESSOR"]
    return {text_processor.lemmatization(tag) for tag in tag_set}


def tag_intersection(tag_set_1, tag_set_2):
    ret_set = set()
    lem_tag_set_1 = lemmatize_tag_set(tag_set_1)
    lem_tag_set_2 = lemmatize_tag_set(tag_set_2)

    for tag_1 in lem_tag_set_1:
        for tag_2 in lem_tag_set_2:
            if _overlapping_keywords(tag_1, tag_2):
                ret_set.add(tag_1)

    return ret_set


def calculate_metrics(df):
    def precision(gold_set, generated_set):
        return len(tag_intersection(generated_set, gold_set)) / len(generated_set)

    def recall(gold_set, generated_set):
        try:
            return len(tag_intersection(generated_set, gold_set)) / len(gold_set)
        except ZeroDivisionError:
            return 0

    def lower_set(tag_set):
        return set([tag.lower().lstrip().rstrip() for tag in tag_set])

    df['All'] = df['All'].apply(tag_preprocessing)
    df['Primary'] = df['Primary'].apply(tag_preprocessing)
    df['Secondary'] = df['Secondary'].apply(tag_preprocessing)

    df['Generated'] = df['Generated'].apply(lower_set)

    df['Primary Precision'] = df.apply(lambda row: precision(row['Primary'], set(row['Generated'])), axis=1)
    df['Primary Recall'] = df.apply(lambda row: recall(row['Primary'], set(row['Generated'])), axis=1)
    df['Secondary Precision'] = df.apply(lambda row: precision(row['Secondary'], set(row['Generated'])), axis=1)
    df['Secondary Recall'] = df.apply(lambda row: recall(row['Secondary'], set(row['Generated'])), axis=1)
    df['Precision'] = df.apply(lambda row: precision(row['All'], set(row['Generated'])), axis=1)
    df['Recall'] = df.apply(lambda row: recall(row['All'], set(row['Generated'])), axis=1)

    return df


def f1_score(prec, rec):
    return 2 * (prec * rec) / (prec + rec)


def print_metrics(df):
    means = df.mean()

    print("#" * 70)
    print(f"\tPrimary Precision: {means['Primary Precision']}")
    print(f"\tPrimary Recall: {means['Primary Recall']}")
    print(f"\tPrimary F1-score: {f1_score(means['Primary Precision'], means['Primary Recall'])}")
    print(f"\tSecondary Precision: {means['Secondary Precision']}")
    print(f"\tSecondary Recall: {means['Secondary Recall']}")
    print(f"\tSecondary F1-score: {f1_score(means['Secondary Precision'], means['Secondary Recall'])}")
    print(f"\tPrecision: {means['Precision']}")
    print(f"\tRecall: {means['Recall']}")
    print(f"\tF1-score: {f1_score(means['Precision'], means['Recall'])}")
    print("#" * 70)


if __name__ == "__main__":
    df = merge_services()

    join_tags(df)  # Join the tags to primary and secondary between annotators

    get_tags_of_services(df, max_num=6)  # Add a column containing the generated tags

    df = df.drop(columns=[column for column in df.columns if "Gold" in column])
    df = calculate_metrics(df)

    df.to_csv(JOINED_ANNOTATIONS, index=False)  # Store the tags for further analysis

    print_metrics(df)
