/*!
 * Start Bootstrap - Agency v7.0.12 (https://startbootstrap.com/theme/agency)
 * Copyright 2013-2023 Start Bootstrap
 * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-agency/blob/master/LICENSE)
 */
//
// Scripts
//

window.addEventListener("DOMContentLoaded", (event) => {
  const form = document.querySelector("form");
  form.addEventListener("submit", (event) => {
    event.preventDefault(); // prevent the form from submitting normally

    const formData = new FormData(form); // create a new FormData object from the form data
    fetch("/upload", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json()) // parse the response as JSON
      .then((data) => {
        console.log(data); // log the response data to the console
        // generate the pie chart
        const likes_given = data["likes_given_of_matches"];
        const likes_received = data["likes_received_of_matches"];
        const dataArray = [likes_given, likes_received];
        generatePieChart(dataArray);

        // create a sentence with the response data
        const num_matches = data["num_matches"];
        const pick_rate = (likes_given / num_matches * 100).toFixed(2);
        const sentence = `Out of ${num_matches} potential suitors, you picked ${pick_rate}%`;

        // display the number of picks from matches
        const numMatchesParagraph = document.getElementById("num_matches");
        numMatchesParagraph.textContent = sentence;

        // display the visualization section
        const visualizationSection = document.getElementById("visualization");
        visualizationSection.style.display = "block";

        // delay the scrolling until the visualization section is fully displayed
        setTimeout(() => {
          window.scrollTo({
            top: visualizationSection.offsetTop,
            behavior: "smooth"
          }); // scroll to the visualization section
          window.location.hash = "visualization"; // update the URL with the ID of the visualization section
        }, 100);
      })
      .catch((error) => {
        console.error(error); // log any errors to the console
        // handle the error
      });
  });

  
  function generatePieChart(dataArray) {
    const data = {
      labels: [
        'Given',
        'Received'
      ],
      datasets: [{
        label: 'My First Dataset',
        data: dataArray,
        backgroundColor: [
          'rgb(255, 99, 132)',
          'rgb(54, 162, 235)',
          'rgb(255, 205, 86)'
        ],
        hoverOffset: 4
      }]
    };
    
    const config = {
      type: 'pie',
      data: data,
      options: {
        plugins: {
          title: {
            display: true,
            text: 'Likes Given vs Received of Matches'
          }
        }
      }
    };

    const myChart = new Chart(
      document.getElementById('myChart'),
      config
    );
  }

  // Navbar shrink function
  var navbarShrink = function () {
    const navbarCollapsible = document.body.querySelector("#mainNav");
    if (!navbarCollapsible) {
      return;
    }
    if (window.scrollY === 0) {
      navbarCollapsible.classList.remove("navbar-shrink");
    } else {
      navbarCollapsible.classList.add("navbar-shrink");
    }
  };

  // Shrink the navbar
  navbarShrink();

  // Shrink the navbar when page is scrolled
  document.addEventListener("scroll", navbarShrink);

  //  Activate Bootstrap scrollspy on the main nav element
  const mainNav = document.body.querySelector("#mainNav");
  if (mainNav) {
    new bootstrap.ScrollSpy(document.body, {
      target: "#mainNav",
      rootMargin: "0px 0px -40%",
    });
  }

  // Collapse responsive navbar when toggler is visible
  const navbarToggler = document.body.querySelector(".navbar-toggler");
  const responsiveNavItems = [].slice.call(
    document.querySelectorAll("#navbarResponsive .nav-link")
  );
  responsiveNavItems.map(function (responsiveNavItem) {
    responsiveNavItem.addEventListener("click", () => {
      if (window.getComputedStyle(navbarToggler).display !== "none") {
        navbarToggler.click();
      }
    });
  });
});
