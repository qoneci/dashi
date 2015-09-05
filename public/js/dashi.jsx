/**
dashboard for presentation of test results in this case from jenkins
*/
var Col = ReactBootstrap.Col;

var TimerSinceUpdate = React.createClass({
    getInitialState: function() {
      return {elapsed: 0};
    },
    componentDidMount: function() {
      this.timer = setInterval(this.tick, 50);
    },
    componentWillUnmount: function() {
      clearInterval(this.timer);
    },
    tick: function() {
      this.setState({elapsed: new Date() - this.props.start});
    },
    render: function() {
      var elapsed = Math.round(this.state.elapsed / 100);
      var seconds = (elapsed / 10).toFixed(1);
      return <p>{seconds}</p>;
    }
});

var TimerBlock = React.createClass({
  render: function() {
    return (
      <Col className='dashi-card-size dashi-card-white dashi-card-size-mid'>
        <div className='dashi-card-text-timer'>
          <TimerSinceUpdate start={Date.now()} />
        </div>
      </Col>
    );
  }
});

var ResultBlock = React.createClass({
  render: function() {
    return (
      <Col className={this.props.colCss}>
        <div className='dashi-card-text'>
          <div>
            <b>
              {this.props.name}
            </b>
          </div>
          <div>
            pass: {this.props.pass}
          </div>
          <div>
            fail: {this.props.fail}
          </div>
          <div>
            build: {this.props.build}
          </div>
          <div>
            buildTime: {this.props.buildTime}
          </div>
          <div>
            result: {this.props.buildResult}
          </div>
          <div>
            <a href="{this.props.buildLink}">link</a>
          </div>
        </div>
      </Col>
    );
  }
});

var testStatus = function(buildResult) {
  classString = 'dashi-card-size dashi-card-size-mid'
  if (buildResult === 'SUCCESS') {
    return classString += ' dashi-card-pass';
  }
  else if (buildResult === 'FAILURE') {
    return classString += ' dashi-card-fail'
  }
  else if (buildResult === 'UNSTABLE') {
    return classString += ' dashi-card-warn';
  }
  else if (buildResult === 'ABORTED') {
    return classString += ' dashi-card-grey';
  }
  else {
    return classString += ' dashi-card-grey';
  }
}

var ResultList = React.createClass({
    render: function() {
      var resultNodes = this.props.data.map(function (s) {
        var testResult = testStatus(s.result);
        return (
          <ResultBlock name={s.name}
                       pass={s.pass}
                       fail={s.fail}
                       build={s.build}
                       colCss={testResult}
                       buildTime={s.buildDurationInSec}
                       buildResult={s.result}
                       buildLink={s.buildLink}/>
        );
      });
      const navInstance = (
        <div className='container-fluid'>
          {resultNodes}
          <TimerBlock />
        </div>
      );
      return (
        navInstance
      );
    }
});

var ResultContainer = React.createClass({
  loadCommentsFromServer: function() {
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    this.loadCommentsFromServer();
    setInterval(this.loadCommentsFromServer, this.props.pollInterval);
  },
  render: function() {
    return (
      <div className="resultContainer">
        <ResultList data={this.state.data} />
      </div>
    );
  }
});

React.render(
  <ResultContainer url="/api/result" pollInterval={15000} />,
  document.getElementById('content')
);
