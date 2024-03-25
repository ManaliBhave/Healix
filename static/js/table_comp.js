document.addEventListener("DOMContentLoaded", function() {
    var selectedMaxRows = 10; // Variable to store the selected number of rows

    getPagination('#table-id');
    document.getElementById('maxRows').dispatchEvent(new Event('change'));

    function getPagination(table) {
        document.getElementById('maxRows').addEventListener('change', function() {
            selectedMaxRows = parseInt(this.value); // Update the selected number of rows
            document.querySelector('.pagination').innerHTML = ''; // reset pagination div
            var trnum = 0; // reset tr counter 
            var maxRows = parseInt(this.value); // get Max Rows from select option

            var totalRows = document.querySelectorAll(table + ' tbody tr').length - 1; // numbers of rows excluding header
            document.querySelectorAll(table + ' tr').forEach(function(row, index) { // each TR in table
                if (index !== 0) { // exclude header row
                    trnum++; // Start Counter 
                    if (trnum > maxRows) { // if tr number gt maxRows
                        row.style.display = 'none'; // hide it
                    }
                    if (trnum <= maxRows) {
                        row.style.display = ''; // show it
                    }
                }
            });

            if (totalRows > maxRows) { // if tr total rows gt max rows option
                var pagenum = Math.ceil(totalRows / maxRows); // ceil total(rows/maxrows) to get ..  
                // numbers of pages 
                for (var i = 1; i <= pagenum;) { // for each page append pagination li 
                    var li = document.createElement('li');
                    li.setAttribute('data-page', i);
                    li.innerHTML = '<span>' + i++ + '<span class="sr-only"></span></span>';
                    document.querySelector('.pagination').appendChild(li);
                } // end for i 
            } // end if row count > max rows
            document.querySelector('.pagination li:first-child').classList.add('active'); // add active class to the first li 

            //SHOWING ROWS NUMBER OUT OF TOTAL DEFAULT
            showig_rows_count(maxRows, 1, totalRows + 1);
            //SHOWING ROWS NUMBER OUT OF TOTAL DEFAULT

            document.querySelectorAll('.pagination li').forEach(function(item) {
                item.addEventListener('click', function(e) { // on click each page
                    e.preventDefault();
                    var pageNum = this.getAttribute('data-page'); // get it's number
                    var trIndex = 0; // reset tr counter
                    document.querySelectorAll('.pagination li').forEach(function(el) { // remove active class from all li 
                        el.classList.remove('active');
                    });
                    this.classList.add('active'); // add active class to the clicked 

                    //SHOWING ROWS NUMBER OUT OF TOTAL
                    showig_rows_count(maxRows, pageNum, totalRows + 1);
                    //SHOWING ROWS NUMBER OUT OF TOTAL

                    document.querySelectorAll(table + ' tr').forEach(function(row, index) { // each tr in table
                        if (index !== 0) { // exclude header row
                            trIndex++; // tr index counter 
                            // if tr index gt maxRows*pageNum or lt maxRows*pageNum-maxRows fade if out
                            if (trIndex > (maxRows * pageNum) || trIndex <= ((maxRows * pageNum) - maxRows)) {
                                row.style.display = 'none';
                            } else {
                                row.style.display = ''; // show it
                            }
                        }
                    }); // end of for each tr in table
                }); // end of on click pagination list
            });

        }); // end of on select change 

        // END OF PAGINATION 
    }

    // SI SETTING
    window.onload = function() {
        default_index();
    };

    //ROWS SHOWING FUNCTION
    function showig_rows_count(maxRows, pageNum, totalRows) {
        //Default rows showing
        var end_index = maxRows * pageNum;
        var start_index = ((maxRows * pageNum) - maxRows) + parseFloat(1);
        var string = 'Showing ' + start_index + ' to ' + end_index + ' of ' + totalRows + ' entries';
        document.querySelector('.rows_count').innerHTML = string;
    }

    // CREATING INDEX
    function default_index() {
        var table = document.querySelector('table');
        var id = 0;
        var rows = table.querySelectorAll('tr');
        rows[0].insertAdjacentHTML('afterbegin', '<th> ID </th>');

        for (var i = 1; i < rows.length; i++) {
            id++;
            rows[i].insertAdjacentHTML('afterbegin', '<td>' + id + '</td>');
        }
    }

    // All Table search script
    function FilterkeyWord_all_table() {
        var input = document.getElementById("search_input_all");
        var filter = input.value.toLowerCase();
        var table = document.getElementById("table-id");
        var tr = table.getElementsByTagName("tr");

        var visibleRows = 0; // Counter for visible rows
        for (var i = 1; i < tr.length; i++) {
            var flag = false;
            var tds = tr[i].getElementsByTagName("td");
            for (var j = 0; j < tds.length; j++) {
                var td = tds[j];
                if (td.innerHTML.toLowerCase().indexOf(filter) > -1) {
                    flag = true;
                    break;
                }
            }
            if (flag) {
                tr[i].style.display = "";
                visibleRows++; // Increment counter for each visible row
            } else {
                tr[i].style.display = "none";
            }
        }

        // Reset pagination to show selected number of rows
        var maxRows = selectedMaxRows;
        var totalRows = visibleRows;
        var pagenum = Math.ceil(totalRows / maxRows);
        document.querySelector('.pagination').innerHTML = ''; // reset pagination div
        for (var i = 1; i <= pagenum;) { // for each page append pagination li 
            var li = document.createElement('li');
            li.setAttribute('data-page', i);
            li.innerHTML = '<span>' + i++ + '<span class="sr-only"></span></span>';
            document.querySelector('.pagination').appendChild(li);
        } // end for i 
        document.querySelector('.pagination li:first-child').classList.add('active'); // add active class to the first li 

        //SHOWING ROWS NUMBER OUT OF TOTAL DEFAULT
        showig_rows_count(maxRows, 1, totalRows);
        //SHOWING ROWS NUMBER OUT OF TOTAL DEFAULT

        document.querySelectorAll('.pagination li').forEach(function(item) {
            item.addEventListener('click', function(e) { // on click each page
                e.preventDefault();
                var pageNum = this.getAttribute('data-page'); // get it's number
                var trIndex = 0; // reset tr counter
                document.querySelectorAll('.pagination li').forEach(function(el) { // remove active class from all li 
                    el.classList.remove('active');
                });
                this.classList.add('active'); // add active class to the clicked 

                //SHOWING ROWS NUMBER OUT OF TOTAL
                showig_rows_count(maxRows, pageNum, totalRows);
                //SHOWING ROWS NUMBER OUT OF TOTAL

                document.querySelectorAll(table + ' tr').forEach(function(row, index) { // each tr in table
                    if (index !== 0) { // exclude header row
                        trIndex++; // tr index counter 
                        // if tr index gt maxRows*pageNum or lt maxRows*pageNum-maxRows fade if out
                        if (trIndex > (maxRows * pageNum) || trIndex <= ((maxRows * pageNum) - maxRows)) {
                            row.style.display = 'none';
                        } else {
                            row.style.display = ''; // show it
                        }
                    }
                }); // end of for each tr in table
            }); // end of on click pagination list
        });
    }

    // Call the search function whenever the search input changes
    document.getElementById("search_input_all").addEventListener("input", function() {
        FilterkeyWord_all_table();

        // Reset table if search input is blank
        if (this.value.trim() === '') {
            document.getElementById('maxRows').dispatchEvent(new Event('change'));
        }
    });
});
