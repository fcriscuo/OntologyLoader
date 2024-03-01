from journal_article_loader import journal_artical_embedding_processor as jaep

def test_get_journal_article_abstract(pmid:int):
    """
    Test the get_journal_article_abstract function
    """
    pubmed_id = "12345"
    print(jaep.get_journal_article_abstract(pmid))
    return

if __name__ == "__main__":

    test_get_journal_article_abstract(22972962)
