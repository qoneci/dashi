/**
dashboard for presenting test results in this case from jenkins
*/
var Col = ReactBootstrap.Col;
var Row = ReactBootstrap.Row;
var Grid = ReactBootstrap.Grid;

var ResultBlock = function ({
    <Col xs={6} md={3}>
      name: {this.props.name} pass: {this.props.pass} fail: {this.props.fail} build: {this.props.build}
    <Col>
  );
});

var ResultList = React.createClass({
    render: function() {
      var resultNodes = this.props.data.map(function (s) {
        return (
          <Row>
            <ResultBlock name={s.name} pass={s.pass} fail={s.fail} build={s.build} />
          </Row>
        );
      });
      return (
        <div className="resultBlock">
          <Grid>
            {resultNodes}
          </Grid>
        </div>
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
  <ResultContainer url="/api/result" pollInterval={20000} />,
  document.getElementById('content')
);
