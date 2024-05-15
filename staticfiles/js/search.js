$(document).ready(function() {
    const container = $('.search-results-container');

    function highlightMatch(text, query) {
        const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const words = escapedQuery.split(/\s+/).filter(Boolean); 

        const regexPattern = `\\b(${words.join('|')})\\b`;

        const regex = new RegExp(regexPattern, 'gi'); 
        return text.replace(regex, '<span class="highlight-search">$&</span>');
    }

    function updateSearchResults(query) {
        if (query.length > 0) {  
            $.ajax({
                url: '/search/',  
                method: 'GET',
                data: { query: query },
                success: function(response) {
                    const shopItems = response.shop_items;
                    container.empty();

                    if (shopItems.length > 0) {
                        shopItems.forEach(item => {
                            const highlightedTitle = highlightMatch(item.title, query);
                            const highlightedCategory = highlightMatch(item.category, query);
                            const highlightedSubject = highlightMatch(item.subject, query);
                            const highlightedEducationLevel = highlightMatch(item.education_level, query);

                            const itemDetailUrl = `/${item.category_slug}/${item.id}/${item.slug}/`;

                            const card = `
                                <div class="mb-3">
                                    <div class="card">
                                        <div class="card-body">
                                            <h5 class="card-title">
                                                <a href="${itemDetailUrl}" style="font-size: 18px; text-decoration: none; color: blue;">
                                                    ${highlightedTitle}
                                                </a>
                                            </h5>
                                            <div class="row">
                                                <div class="col">
                                                    <p class="card-text"><strong>Category</strong>: ${highlightedCategory}</p>
                                                </div>
                                                <div class="col">
                                                    <p class="card-text"><strong>Subject</strong>: ${highlightedSubject}</p>
                                                </div>
                                                <div class="col">
                                                    <p class="card-text"><strong>Level</strong>: ${highlightedEducationLevel}</p>
                                                </div>
                                                <div class="col">
                                                    <p class="card-text"><strong>Price</strong>: Ksh ${item.price}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `;
                            container.append(card);
                        });
                        container.show(); 
                    } else {
                        container.html('<p>No results matched your query.</p>');
                        container.show();  
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error fetching search results:', error);
                }
            });
        } else {
            container.hide();  
        }
    }

    $('#site-wide-search-form input[type="text"]').on('input', function() {
        const query = $(this).val().trim();
        updateSearchResults(query);
    });

    $(document).on('click', function(event) {
        if (!$(event.target).closest('#site-wide-search-form').length && !$(event.target).closest('.search-results-container').length) {
            container.hide();
        }
    });

    $('#site-wide-search-form input[type="text"]').on('keyup', function() {
        const query = $(this).val().trim();
        if (query === '') {
            container.hide();
        }
    });

    container.hide();
});
