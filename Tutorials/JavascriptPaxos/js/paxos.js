// First, checks if it isn't implemented yet.
if (!String.prototype.format) {
    String.prototype.format = function () {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function (match, number) {
            return typeof args[number] != 'undefined'
              ? args[number]
              : match
            ;
        });
    };
}

function ProposerServer(name, serverId) {
    var self = this;
    self.name = ko.observable(name);
    self.serverId = ko.observable(serverId);
    self.submittedValue = ko.observable("");
    self.maxRound = ko.observable(0);
    self.proposedValue = ko.observable("");
    self.proposalNumber = ko.observable(null);

    self.PrepareResponses = [];
    self.AcceptResponses = [];
    self.AcceptServers = [];

    self.messageQueue = ko.observableArray([]);
    self.messageCount = ko.computed(function () {
        return self.messageQueue().length;
    });

    self.ReadMsg = function () {
        if (self.messageQueue().length > 0) {
            var msg = self.messageQueue()[0];
            self.messageQueue.remove(msg);
            if (msg instanceof PrepareResponse) {
                self.OnPrepareResponse(msg);
            }
            if (msg instanceof AcceptResponse) {
                self.OnAcceptResponse(msg);
            }

        }
    }

    self.ClearMsg = function () {
        self.messageQueue.removeAll();
    }

    self.OnAcceptResponse = function (msg) {
        self.AcceptResponses.push(msg);


        if (self.AcceptResponses.length >= Math.floor(self.AcceptServers.length / 2) + 1) {
            var failure = false;
            for (var index = 0; index < self.AcceptResponses.length; index++) {
                if (self.AcceptResponses[index].MinProposal > self.proposalNumber()) {
                    failure = true;
                }
            }
        }
        if (failure) {
            self.submittedValue(self.proposedValue());
            self.submitValue();
        }
    }

    self.OnPrepareResponse = function (msg) {
        self.PrepareResponses.push(msg);

        if (self.PrepareResponses.length >= Math.floor(self.AcceptServers.length / 2) + 1) {

            var highestProposal = 0;
            var newValue = "";
            for (var indx = 0; indx < self.PrepareResponses.length; indx++) {
                var respObject = self.PrepareResponses[indx];
                if (respObject.acceptedProposal != null && respObject.acceptedProposal > highestProposal) {
                    highestProposal = respObject.acceptedProposal;
                    newValue = respObject.acceptedValue;
                }
            }

            if (highestProposal > 0) {
                self.proposedValue(newValue);
            }

            var acceptMsg = new AcceptMsg(self.proposalNumber(), self.proposedValue(), self);
            for (var indx = 0; indx < self.AcceptServers.length; indx++) {
                var respObject = self.AcceptServers[indx];
                respObject.messageQueue.push(acceptMsg);
            }
            self.PrepareResponses = [];

        }

    }

    self.submitValue = function () {
        self.maxRound(self.maxRound() + 1);
        self.proposalNumber(self.maxRound() * 10 + self.serverId());
        self.proposedValue(self.submittedValue());
        self.submittedValue("");

        prepMsg = new PrepareMsg(self.proposalNumber(), self)

        for (var index = 0; index < self.AcceptServers.length; index++) {
            self.AcceptServers[index].messageQueue.push(prepMsg);
        }
    }
}

function AcceptorServer(name, ttRow) {
    var self = this;
    self.name = name;
    self.minProposal = ko.observable(0);
    self.acceptedValue = ko.observable("");
    self.acceptedProposal = ko.observable(null);
    self.row = ttRow;

    self.messageQueue = ko.observableArray([]);
    self.messageCount = ko.computed(function () {
        return self.messageQueue().length;
    });

    self.ReadMsg = function () {
        if (self.messageQueue().length > 0) {
            var msg = self.messageQueue()[0];
            self.messageQueue.remove(msg);
            if (msg instanceof PrepareMsg) {
                self.OnPrepare(msg);
            }
            if (msg instanceof AcceptMsg) {
                self.OnAccept(msg);
            }
        }
    }

    self.ClearMsg = function () {
        self.messageQueue.removeAll();
    }

    self.OnPrepare = function(msg) {

        if (msg.ProposalNumber > self.minProposal()) {
            self.minProposal(msg.ProposalNumber);
            
            reply = new PrepareResponse(self.acceptedValue(), self.acceptedProposal(), self);
            msg.From.messageQueue.push(reply);

            for (var row = 0; row < self.TimeTable().length; row++) {
                if (row == self.row) {
                    self.TimeTable()[row].Columns.push("P {0}".format(msg.ProposalNumber));
                }
                else {
                    self.TimeTable()[row].Columns.push("");
                }
            }
            
        }
    }

    self.OnAccept = function (msg) {

        if (msg.ProposalNumber >= self.minProposal())
        {
            self.minProposal(msg.ProposalNumber);
            self.acceptedProposal(msg.ProposalNumber);
            self.acceptedValue(msg.ProposedValue);

            for (var row = 0; row < self.TimeTable().length; row++) {
                if (row == self.row) {
                    self.TimeTable()[row].Columns.push("A {0}:{1}".format(msg.ProposalNumber, msg.ProposedValue));
                }
                else {
                    self.TimeTable()[row].Columns.push("");
                }
            }


        }
        var acceptResponse = new AcceptResponse(self.minProposal(), self.acceptedValue(), this);
        msg.From.messageQueue.push(acceptResponse);

    }

}

function AcceptResponse(minProposal, acceptedValue, Server) {
    var self = this;
    self.MinProposal = minProposal;
    self.AcceptedValue = acceptedValue;
    self.From = Server;

    self.OutputInfo = ko.computed(function () {
        return "Accept Response {0} {1}".format(self.MinProposal, self.AcceptedValue);
    });

}

function AcceptMsg(ProposalNumber, ProposedValue, Server) {
    var self = this;
    self.ProposalNumber = ProposalNumber;
    self.ProposedValue = ProposedValue;
    self.From = Server;

    self.OutputInfo = ko.computed(function () {
        return "Accept {0} {1}".format(self.ProposalNumber, self.ProposedValue);
    });


}

function PrepareMsg(ProposalNumber, Server) {
    var self = this;
    self.ProposalNumber = ProposalNumber;
    self.From = Server;

    self.OutputInfo = ko.computed(function () {
        return "Prepare {0}".format(self.ProposalNumber);
    });

}

function PrepareResponse(acceptedValue, acceptedProposal, fromServer) {
    var self = this;
    self.acceptedValue = acceptedValue;
    self.acceptedProposal = acceptedProposal;
    self.From = fromServer;

    self.OutputInfo = ko.computed(function () {
        return "Prepare Response {0} {1}".format(self.acceptedProposal, self.acceptedValue);
    });

}

function column() {
    var self = this;
    self.Columns = ko.observableArray();
}

function PaxosViewModel() {

    var self = this;

    self.Acceptors = ko.observableArray([
        new AcceptorServer("Acceptor 1", 0),
        new AcceptorServer("Acceptor 2", 1),
        new AcceptorServer("Acceptor 3", 2)
    ]);

    self.TimeTable = ko.observableArray();
    for (var index = 0; index < self.Acceptors().length; index++) {
        self.TimeTable.push( new column() );
    }
    for (var index = 0; index < self.Acceptors().length; index++) {
        self.Acceptors()[index].TimeTable = self.TimeTable;
    }

    self.Proposers = ko.observableArray([
        new ProposerServer("Observer", 1), 
        new ProposerServer("Observer", 2)
    ]);
    self.Proposers()[0].AcceptServers.push(self.Acceptors()[0]);
    self.Proposers()[0].AcceptServers.push(self.Acceptors()[1]);
    self.Proposers()[0].AcceptServers.push(self.Acceptors()[2]);

    self.Proposers()[1].AcceptServers.push(self.Acceptors()[0]);
    self.Proposers()[1].AcceptServers.push(self.Acceptors()[1]);
    self.Proposers()[1].AcceptServers.push(self.Acceptors()[2]);

    for (var index = 0; index < self.Proposers().length; index++) {
        self.Proposers()[index].TimeTable = self.TimeTable;
    }

}