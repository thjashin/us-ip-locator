// -------- Class that interpret with MapSearch server --------
function MapSearchAPI()
{
  var self = this;

  // Logger when an error occurred.
  this.error_handler = function(msg) {
    alert(msg);
  };

  // Do query on given query, and call cb(results) on success.
  this.query = function(query, cb) {
    $.ajax({
      url: "/query/",
      type: "POST",
      dataType: "json",
      contentType: "application/json",
      data: $.toJSON({query: $('#q').val()}),
      success: function(data) {
        if (data['error'] != 0) {
          self.error_handler('查询失败: ' + data['message']);
          return;
        }
        matches = [];
        $.each(data['results'], function (i, o) {
          matches.push(o);
        });
        cb(matches);
      },
      error: function(data) {
        self.error_handler('查询失败: 网络错误');
      }
    });
  };

  return this;
}

// -------- Class that manages instance of Google map ---------
function ResultMap(canvas) {
  var self = this;

  this.canvas = canvas;
  this.markers = [];

  // Add an info window to given marker, and bind events.
  function GMarker(title, description, pos, draggable, icon, zIndex) {
    var marker = new google.maps.Marker({
      position: new google.maps.LatLng(pos[0], pos[1]),
      draggable: draggable,
      clickable: true,
      title: title,
      icon: icon || 'http://maps.google.com/mapfiles/marker.png',
      zIndex: zIndex || 99,
      animation: google.maps.Animation.DROP
    });
    marker.info = new google.maps.InfoWindow({
      content: description
    });
    marker.info_visible = false;
    marker.show_info = function() {
      marker.info.open(self.map, marker);
      marker.info_visible = true;
    };
    marker.hide_info = function() {
      marker.info.close();
      marker.info_visible = false;
    };
    google.maps.event.addListener(marker, 'click', function() {
      if (marker.info_visible) {
        marker.hide_info();
      } else {
        marker.show_info();
      }
    });
    marker.setMap(self.map);
    return marker;
  }

  // Create the map at |center|.
  var low = new google.maps.LatLng(49, -130);
  var high = new google.maps.LatLng(25, -70);
  var bounds = new google.maps.LatLngBounds(low, high);

  var mapOptions = {
    // center: new google.maps.LatLng(center[0], center[1]),
    // zoom: 12
    center: bounds.getCenter(),
    zoom: 4
  };
  this.map = new google.maps.Map(canvas, mapOptions);

  // When click on map, I'd like to clear all info window.
  google.maps.event.addListener(self.map, 'click', function(event) {
    self.clearInfo();
  });

  // Clear all marker info windows.
  this.clearInfo = function() {
    for (var i=0; i<self.markers.length; ++i) {
      self.markers[i].hide_info();
    }
  };

  // Get the icon for POI at k.
  this.getMarkerIcon = function(k) {
    return 'http://maps.google.com/mapfiles/marker' + 
      String.fromCharCode(k+65) + '.png';
  };

  // Set markers for given POIs.
  var setMarkersInterval = null;

  this.fitBounds = function(pois) {
    if (pois.length == 0)
        return;

    // Zoom the map to perfect view.
    var leftTop = [pois[0]['pos'][0], pois[0]['pos'][1]],
        rightBottom = [pois[0]['pos'][0], pois[0]['pos'][1]];

    for (var i=1; i<pois.length; ++i) {
      var pos = pois[i]['pos'];
      if (pos[0] < leftTop[0]) leftTop[0] = pos[0];
      if (pos[1] < leftTop[1]) leftTop[1] = pos[1];
      if (pos[0] > rightBottom[0]) rightBottom[0] = pos[0];
      if (pos[1] > rightBottom[1]) rightBottom[1] = pos[1];
    }

    // prevent from too small points
    if (pois.length == 1) {
        for (var i=0; i<1; ++i) {
            leftTop[i] -= 0.1;
            rightBottom[i] += 0.1;
        }
    }

    var bounds = new google.maps.LatLngBounds(
      new google.maps.LatLng(leftTop[0], leftTop[1]),
      new google.maps.LatLng(rightBottom[0], rightBottom[1])
    );

    self.map.fitBounds(bounds);
  };

  this.setMarkers = function(pois) {
    // Clear old markers.
    if (setMarkersInterval) {
      clearInterval(setMarkersInterval);
      setMarkersInterval = null;
    }
    for (var i=0; i<self.markers.length; ++i) {
      self.markers[i].hide_info();
      self.markers[i].setMap(null);
    }
    self.markers = [];

    // Template string that renders loaded POI.
    var template = 
      '<div class="info-poi">' +
      '<div class="title">IP: <% ip %></div>' +
      '<div class="desc">Location: <% desc %></div>' +
      '</div>'
    ;

    // The template function that renders loaded POI.
    function render(o) {
      return template.replace(/<%\s*(\w+)\s*%>/g, function (match, p1) {
        return o[p1];
      });
    };

    // Add new markers one by one, waiting for 100ms each.
    var nextId = 0;
    var pois_saved = [];
    for (var i=0; i<pois.length; ++i) {
      pois_saved.push(pois[i]);
    }

    setMarkersInterval = setInterval(function() {
      if (nextId >= pois_saved.length) {
        clearInterval(setMarkersInterval);
        setMarkersInterval = null;

        // Show the information of 'A'
        /*if (self.markers && self.markers[0])
          self.markers[0].show_info();*/
        return;
      }

      var o = pois_saved[nextId];
      marker = new GMarker(o['title'], render(o), o['pos'], false,
                           self.getMarkerIcon(nextId), 98-nextId);
      self.markers.push(marker);

      nextId++
    }, 100);
  };

  return this;
}

// -------- Instances of classes, and the initializer ---------
function MapController() {
  var self = this;

  var searcher = new MapSearchAPI();
  var statusUI;
  var resultMap = null;
  var current_query = null;

  function update_map(q) {
    current_query = q || current_query;

    // Do query only if |query| is not null.
    if (current_query) {
      resultMap.clearInfo();
      searcher.query(current_query,
        function (pois) {
          resultMap.fitBounds(pois);
          resultMap.setMarkers(pois);
        }
      );
    }
  }

  function init_map() {
    // Create the map instance.
    resultMap = new ResultMap(document.getElementById('map_canvas'));
  }

  init_map([0, 0]);

  $('#q').val('');
  $('#q').focus();
  $('#search').click(function() {
    update_map($('#q').val());
  });
  $('#q').keypress(function(event) {
    if (event.which == 13) {
      event.preventDefault();
      update_map($('#q').val());
    }
  });

  return this;
}