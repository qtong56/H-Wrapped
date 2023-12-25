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

        // TODO: Game Time Stats
        const likes_given = data["likes_given_of_matches"];
        const likes_received = data["likes_received_of_matches"];
        const num_matches = data["num_matches"];
        const pick_rate = (likes_given / num_matches * 100).toFixed(2);
        
        const overview = document.getElementById("overview");
        const overview_sentences = `Over the past year, you talked to ${num_matches} people. 
              Out of those, you chose ${pick_rate}%. You liked [number of likes 
                that didn’t match] many people that didn’t like you back.`
        overview.textContent = overview_sentences;

        // generate pie chart
        const dataArray = [likes_given, likes_received];
        generatePieChart(dataArray);

        // TODO: Chatting Stats
        // show number of messages sent
        const num_messages = data['total_messages_sent'];
        const weekday = data['most_freq_weekday'];
        const hours = data['most_freq_hour'];
        
        // Extract timestamps and values from the data
        timeSeriesData = JSON.parse(data['monthly_message_lengths']);
        const timestamps = timeSeriesData.map(entry => new Date(entry.Timestamp).toLocaleDateString('default', { month: 'long' }));
        const values = timeSeriesData.map(entry => entry.BodyLength);

        // generate the line chart
        const ctx = document.getElementById('messagefreq').getContext('2d');
        generateMessageLengthChart(ctx, timestamps, values);

        // Find the entry with the highest body length
        const entryWithHighestBodyLength = timeSeriesData.reduce((prev, current) => {
          return (prev.BodyLength > current.BodyLength) ? prev : current;
        });
        // Get the month of the timestamp with the highest body length
        const monthOfHighestBodyLength = new Date(entryWithHighestBodyLength.Timestamp).toLocaleString('default', { month: 'long' });

        const chatstats = document.getElementById("chat_stats");
        chatstats.textContent = `You sent ${num_messages} messages, and were most 
        active in the month of ${monthOfHighestBodyLength}. You chatted the most on ${weekday}s, and 
        sent the longest messages at ${hours}.
        Here were your most used words: `
        
        // top 10 words
        const top_words = data['top5_words'];
        
        // Parse the string into an array
        const wordsArray = JSON.parse(top_words.replace(/'/g, '"'));

        // Get the paragraph element
        const topWordsParagraph = document.getElementById('topwords');

        // Generate a numbered list of words and set it as the content of the paragraph
        const wordsList = wordsArray.map((word, index) => `${index + 1}. ${word}`).join("<br>");
        topWordsParagraph.innerHTML = wordsList;

        // TODO: Expletives
        const profanities = data['profanities'];
        const expletives = document.getElementById('expletives');

        // Generate a numbered list of words and set it as the content of the paragraph
        const profanitiesList = profanities.map((word, index) => `${index + 1}. ${word}`).join("<br>");
        expletives.innerHTML = profanitiesList;

        
        // TODO: Emotional Analysis
        // create emotions barchart
        const emotions = data['emotion_spectrum'];
        const emotionsCTX = document.getElementById('emotions').getContext('2d');
        generateEmotionsChart(emotionsCTX, emotions);

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

  function generateMessageLengthChart(ctx, timestamps, values) {
    // Create the line chart
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: timestamps,
        datasets: [{
          label: 'Messages per Month',
          data: values,
          borderColor: 'blue',
          borderWidth: 1
        }]
      },
      options: {
        scales: {
          x: {
            type: 'time',
            time: {
              unit: 'day',
              displayFormats: {
                day: 'MMM D'
              }
            }
          },
          y: {
            beginAtZero: true
          },
          xAxes: [{
            gridLines: {
              display: false,
            },
          }],
          yAxes: [{
            gridLines: {
              display: false,
            },
          }]
        }
      }
    });
  }


  function generateEmotionsChart(ctx, data) {
    const dataArray = Object.entries(data)
      .sort((a, b) => b[1] - a[1])
      .map(([label, value]) => ({ label, value }));

    const labels = dataArray.map(item => item.label);
    const values = dataArray.map(item => item.value);

    const config = {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Emotions',
          data: values,
          backgroundColor: 'rgb(54, 162, 235)',
          borderWidth: 1
        }]
      },
      options: {
        indexAxis: 'y',
        scales: {
          y: {
            beginAtZero: true
          },
          yAxes: [{
            gridLines: {
              display: false,
            },
          }],
          xAxes: [{
            gridLines: {
              display: false,
            },
          }],
        }
      }
    };

    new Chart(ctx, config);
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
