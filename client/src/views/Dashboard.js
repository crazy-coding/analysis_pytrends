
import React from "react";
// react plugin used to create charts
import { Line } from "react-chartjs-2";
// react plugin used to create DropdownMenu for selecting items
import Select from "react-select";
// react plugin used to create datetimepicker
import ReactDatetime from "react-datetime";
// axios for api
import axios from 'axios';

// reactstrap components
import {
  Card,
  CardHeader,
  CardBody,
  CardTitle,
  Label,
  FormGroup,
  Row,
  Col,
} from "reactstrap";

const SERVER_URI = 'http://127.0.0.1:8000';

var chartOption = {
  maintainAspectRatio: false,
  legend: {
    display: false
  },
  tooltips: {
    backgroundColor: "#f5f5f5",
    titleFontColor: "#333",
    bodyFontColor: "#666",
    bodySpacing: 4,
    xPadding: 12,
    mode: "nearest",
    intersect: 0,
    position: "nearest"
  },
  responsive: true,
  scales: {
    yAxes: [
      {
        barPercentage: 1.6,
        gridLines: {
          drawBorder: false,
          color: "rgba(29,140,248,0.0)",
          zeroLineColor: "transparent"
        },
        ticks: {
          // suggestedMin: 0,
          // suggestedMax: 100,
          padding: 20,
          fontColor: "#9a9a9a"
        }
      }
    ],
    xAxes: [
      {
        barPercentage: 1.6,
        gridLines: {
          drawBorder: false,
          color: "rgba(29,140,248,0.1)",
          zeroLineColor: "transparent"
        },
        ticks: {
          padding: 20,
          fontColor: "#9a9a9a"
        }
      }
    ]
  }
};

class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      chart: {},
      chartOptions: chartOption,
      site: null,
      siteOptions: [],
      trendType: null,
      trendTypeOptions: [],
      trendName: null,
      trendNameOptions: [],
      pullType: { value: "week", label: "Weekly" },
      fromDate: '2018-01-01',
      toDate: '2020-10-01',
    };
  }
  componentDidMount() {
    this.setCategory("site");
  };
  getCategory = async mode => {
    let site = this.state.site ? this.state.site.value : '';
    let trendType = this.state.trendType ? this.state.trendType.value : '';

    await axios.get(`${SERVER_URI}/api/v1/category/?m=${mode}&site=${site}&trend_type=${trendType}`)
    .then(res => {
      const data = res.data;
      switch (mode) {
        case "site":
          this.setState({ siteOptions: data, site: data[0] });
          break;
        case "type":
          this.setState({ trendTypeOptions: data, trendType: data[0] });
          break;
        case "name":
          this.setState({ trendNameOptions: data, trendName: data[0] });
          break;
        default:
      }
    })
  };
  setCategory = async mode => {
    await this.getCategory(mode);
    switch (mode) {
      case "site":
        await this.getCategory("type");
        await this.getCategory("name");
        break;
      case "type":
        await this.getCategory("name");
        break;
      case "name":
        break;
      default:
    }
    await this.renderChart();
  };
  renderChart = async () => {
    let site = this.state.site ? this.state.site.value : '';
    let trendType = this.state.trendType ? this.state.trendType.value : '';
    let trendName = this.state.trendName ? this.state.trendName.value : '';
    let pullType = this.state.pullType ? this.state.pullType.value : '';

    await axios.get(`${SERVER_URI}/api/v1/chart/?from_date=${this.state.fromDate}&to_date=${this.state.toDate}&site=${site}&trend_type=${trendType}&trend_name=${trendName}&pull_type=${pullType}`)
    .then(res => {
      const data = canvas => {
        let ctx = canvas.getContext("2d");
    
        let gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);
    
        gradientStroke.addColorStop(1, "rgba(29,140,248,0.2)");
        gradientStroke.addColorStop(0.4, "rgba(29,140,248,0.0)");
        gradientStroke.addColorStop(0, "rgba(29,140,248,0)"); //blue colors

        return {
          labels: res.data.labels,
          datasets: [
            {
              label: "Google Trend",
              fill: true,
              backgroundColor: gradientStroke,
              borderColor: "#1f8ef1",
              borderWidth: 2,
              borderDash: [],
              borderDashOffset: 0.0,
              pointBackgroundColor: "#1f8ef1",
              pointBorderColor: "rgba(255,255,255,0)",
              pointHoverBackgroundColor: "#1f8ef1",
              pointBorderWidth: 20,
              pointHoverRadius: 4,
              pointHoverBorderWidth: 15,
              pointRadius: 4,
              data: res.data.values
            }
          ]
        };
      }
      this.setState({ chart: data });
    })
  }
  render() {
    return (
      <>
        <div className="content">
          <Row>
            <Col xs="12">
              <Card className="card-chart">
                <CardHeader>
                  <Row>
                    <Col className="text-left" sm="3">
                      <h5 className="card-category">Google Trends</h5>
                      <CardTitle tag="h2">Charts</CardTitle>
                    </Col>
                    <Col sm="9">
                      <Row>
                        <Col lg="3" md="4" sm="6">
                          <FormGroup className="has-label">
                            <label>Trend Site</label>
                            <Select
                              className="react-select"
                              classNamePrefix="react-select"
                              name="site"
                              value={this.state.site}
                              onChange={value => {
                                this.setState({ site: value }, function() { this.setCategory("type") });
                              } }
                              options={this.state.siteOptions}
                              placeholder="Single Select"
                            />
                          </FormGroup>
                        </Col>
                        <Col lg="3" md="4" sm="6">
                          <FormGroup className="has-label">
                            <label>Trend Type</label>
                            <Select
                              className="react-select"
                              classNamePrefix="react-select"
                              name="trend_type"
                              value={this.state.trendType}
                              onChange={value =>{
                                this.setState({ trendType: value }, function() { this.setCategory("name") });
                              } }
                              options={this.state.trendTypeOptions}
                              placeholder="Single Select"
                            />
                          </FormGroup>
                        </Col>
                        <Col lg="3" md="4" sm="6">
                          <FormGroup className="has-label">
                            <label>Trend Name</label>
                            <Select
                              className="react-select"
                              classNamePrefix="react-select"
                              name="trend_name"
                              value={this.state.trendName}
                              onChange={value => 
                                this.setState({ trendName: value }, function() { this.renderChart() })
                              }
                              options={this.state.trendNameOptions}
                              placeholder="Single Select"
                            />
                          </FormGroup>
                        </Col>
                        <Col lg="3" md="4" sm="6">
                          <FormGroup className="has-label">
                            <label>Pull Type</label>
                            <Select
                              className="react-select"
                              classNamePrefix="react-select"
                              name="pull_type"
                              value={this.state.pullType}
                              onChange={value =>
                                this.setState({ pullType: value }, function() { this.renderChart() })
                              }
                              options={[
                                { value: "hour", label: "Hourly" },
                                { value: "day", label: "Daily" },
                                { value: "week", label: "Weekly" },
                                { value: "month", label: "Monthly" },
                                { value: "weekday", label: "Weekdays" },
                              ]}
                            />
                          </FormGroup>
                        </Col>
                        <Col lg="4" md="6" sm="6">
                          <Row>
                            <Label sm="3">From</Label>
                            <Col sm="9">
                              <FormGroup>
                                <ReactDatetime
                                  inputProps={{
                                    className: "form-control",
                                    placeholder: "From Date"
                                  }}
                                  name="from_date"
                                  dateFormat="YYYY-MM-DD"
                                  timeFormat={false}
                                  value={this.state.fromDate}
                                  onChange={value =>
                                    this.setState({ fromDate: value }, function() { this.renderChart() })
                                  } 
                                />
                              </FormGroup>
                            </Col>
                          </Row>
                        </Col>
                        <Col lg="4" md="6" sm="6">
                          <Row>
                            <Label sm="3">To</Label>
                            <Col sm="9">
                              <FormGroup>
                                <ReactDatetime
                                  inputProps={{
                                    className: "form-control",
                                    placeholder: "To Date"
                                  }}
                                  name="to_date"
                                  dateFormat="YYYY-MM-DD"
                                  timeFormat={false}
                                  value={this.state.toDate}
                                  onChange={value =>
                                    this.setState({ toDate: value.format('YYYY-MM-DD') }, function() { this.renderChart() })
                                  } 
                                />
                              </FormGroup>
                            </Col>
                          </Row>
                        </Col>
                      </Row>
                    </Col>
                  </Row>
                </CardHeader>
                <CardBody>
                  <div className="chart-area">
                    <Line
                      data={this.state.chart}
                      options={this.state.chartOptions}
                    />
                  </div>
                </CardBody>
              </Card>
            </Col>
          </Row>
        </div>
      </>
    );
  }
}

export default Dashboard;
